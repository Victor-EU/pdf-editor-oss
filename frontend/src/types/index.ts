/**
 * TypeScript Type Definitions
 */

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface FileResponse {
  fileName: string;
  filePath: string;
  fileSize: number;
  downloadUrl: string;
  originalSize?: number;
  compressionRatio?: number;
}

export interface MergeRequest {
  files: File[];
  outputFileName?: string;
}

export interface SplitRequest {
  file: File;
  splitMode: 'pages' | 'ranges';
  splitPoints: string[];
  outputFileNameBase?: string;
}

export interface CompressRequest {
  file: File;
  compressionProfile: 'web' | 'print';
  outputFileName?: string;
}

export interface ConvertRequest {
  file: File;
  imageFormat: 'png' | 'jpeg' | 'tiff';
  dpi?: number;
  pages?: string;
  outputFileNameBase?: string;
}

export interface ExtractRequest {
  file: File;
  outputFileName?: string;
  includePageNumbers?: boolean;
}

export interface OcrRequest {
  file: File;
  outputFileName?: string;
  language?: string;
  dpi?: number;
  includePageNumbers?: boolean;
  psm?: number;
}

export interface TableExtractRequest {
  file: File;
  outputFileName?: string;
  includeHeaders?: boolean;
}

export type OperationType = 'view' | 'merge' | 'split' | 'compress' | 'convert' | 'extract' | 'ocr' | 'table-extract';

export interface OperationStatus {
  type: OperationType;
  status: 'idle' | 'processing' | 'success' | 'error';
  progress?: number;
  message?: string;
  result?: FileResponse | FileResponse[];
}
