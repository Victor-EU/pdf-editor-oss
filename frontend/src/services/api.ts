/**
 * API Service Layer
 * Handles all HTTP requests to the backend
 */

import axios, { AxiosInstance } from 'axios';
import {
  ApiResponse,
  FileResponse,
  MergeRequest,
  SplitRequest,
  CompressRequest,
  ConvertRequest,
  ExtractRequest,
  OcrRequest,
  TableExtractRequest,
} from '../types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      timeout: 300000,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  async mergePdfs(request: MergeRequest): Promise<ApiResponse<FileResponse>> {
    const formData = new FormData();
    request.files.forEach((file) => {
      formData.append('files', file);
    });
    if (request.outputFileName) {
      formData.append('outputFileName', request.outputFileName);
    }

    const response = await this.client.post<ApiResponse<FileResponse>>('/merge', formData);
    return response.data;
  }

  async splitPdf(request: SplitRequest): Promise<ApiResponse<FileResponse[]>> {
    const formData = new FormData();
    formData.append('file', request.file);
    formData.append('splitMode', request.splitMode);
    request.splitPoints.forEach((point) => {
      formData.append('splitPoints', point);
    });
    if (request.outputFileNameBase) {
      formData.append('outputFileNameBase', request.outputFileNameBase);
    }

    const response = await this.client.post<ApiResponse<FileResponse[]>>('/split', formData);
    return response.data;
  }

  async compressPdf(request: CompressRequest): Promise<ApiResponse<FileResponse>> {
    const formData = new FormData();
    formData.append('file', request.file);

    // Map frontend profiles to backend compression levels
    const profileToLevel: Record<string, string> = {
      'web': 'high',      // Web = High compression (smaller files)
      'print': 'low',     // Print = Low compression (better quality)
      'custom': 'medium'  // Custom = Medium compression (balanced)
    };

    formData.append('compression_level', profileToLevel[request.compressionProfile]);

    if (request.outputFileName) {
      formData.append('output_filename', request.outputFileName);
    }

    const response = await this.client.post<ApiResponse<FileResponse>>('/compress', formData);
    return response.data;
  }

  async convertPdfToImage(request: ConvertRequest): Promise<ApiResponse<FileResponse[]>> {
    const formData = new FormData();
    formData.append('file', request.file);
    formData.append('imageFormat', request.imageFormat);
    if (request.dpi) {
      formData.append('dpi', request.dpi.toString());
    }
    if (request.pages) {
      formData.append('pages', request.pages);
    }
    if (request.outputFileNameBase) {
      formData.append('outputFileNameBase', request.outputFileNameBase);
    }

    const response = await this.client.post<ApiResponse<FileResponse[]>>('/convert', formData);
    return response.data;
  }

  async extractTextFromPdf(request: ExtractRequest): Promise<ApiResponse<FileResponse>> {
    const formData = new FormData();
    formData.append('file', request.file);
    if (request.outputFileName) {
      formData.append('outputFileName', request.outputFileName);
    }
    if (request.includePageNumbers !== undefined) {
      formData.append('includePageNumbers', request.includePageNumbers.toString());
    }

    const response = await this.client.post<ApiResponse<FileResponse>>('/extract', formData);
    return response.data;
  }

  async ocrPdfText(request: OcrRequest): Promise<ApiResponse<FileResponse>> {
    const formData = new FormData();
    formData.append('file', request.file);
    if (request.outputFileName) {
      formData.append('outputFileName', request.outputFileName);
    }
    if (request.language) {
      formData.append('language', request.language);
    }
    if (request.dpi) {
      formData.append('dpi', request.dpi.toString());
    }
    if (request.includePageNumbers !== undefined) {
      formData.append('includePageNumbers', request.includePageNumbers.toString());
    }
    if (request.psm !== undefined) {
      formData.append('psm', request.psm.toString());
    }

    const response = await this.client.post<ApiResponse<FileResponse>>('/ocr', formData);
    return response.data;
  }

  async extractTablesFromPdf(request: TableExtractRequest): Promise<ApiResponse<FileResponse>> {
    const formData = new FormData();
    formData.append('file', request.file);
    if (request.outputFileName) {
      formData.append('outputFileName', request.outputFileName);
    }
    if (request.includeHeaders !== undefined) {
      formData.append('includeHeaders', request.includeHeaders.toString());
    }

    const response = await this.client.post<ApiResponse<FileResponse>>('/table-extract', formData);
    return response.data;
  }

  async downloadFile(filename: string): Promise<Blob> {
    const response = await this.client.get(`/download/${filename}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  triggerDownload(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}

export const apiService = new ApiService();
