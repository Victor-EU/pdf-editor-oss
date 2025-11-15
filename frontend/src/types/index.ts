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
  compressionProfile: 'web' | 'print' | 'custom';
  imageQuality?: number;
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

export type AnnotationType = 'highlight' | 'text' | 'underline' | 'strikeout' |
                              'square' | 'circle' | 'line' | 'arrow' | 'freehand' | 'redact';

export interface Annotation {
  annotation_type: AnnotationType;
  page_number: number;
  coordinates: number[];
  color?: [number, number, number];
  text?: string;
  opacity?: number;
  border_width?: number;
}

export interface AnnotationRequest {
  file: File;
  annotations: Annotation[];
}

export interface RedactionArea {
  page: number;
  rect?: number[];
  text?: string;
}

export interface RedactionRequest {
  file: File;
  redactions: RedactionArea[];
  fill_color?: [number, number, number];
}

export type OperationType = 'view' | 'merge' | 'split' | 'compress' | 'convert' | 'extract' | 'ocr' | 'annotate';

export interface OperationStatus {
  type: OperationType;
  status: 'idle' | 'processing' | 'success' | 'error';
  progress?: number;
  message?: string;
  result?: FileResponse | FileResponse[];
}
