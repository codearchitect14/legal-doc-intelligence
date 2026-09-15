import { Upload } from "lucide-react";
import { useRef, useState } from "react";

import { Button } from "../../components/Button";
import { ApiError, documentsApi } from "../../lib/apiClient";

export function DocumentUpload({ caseId, onUploaded }: { caseId: string; onUploaded: () => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFiles(files: FileList | null) {
    if (!files || files.length === 0) return;
    setUploading(true);
    setError(null);
    try {
      await documentsApi.upload(caseId, files);
      onUploaded();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed. Please try again.");
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".pdf,.docx,.png,.jpg,.jpeg,.tiff,.tif,.bmp,.zip"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
      <Button variant="secondary" onClick={() => inputRef.current?.click()} disabled={uploading}>
        <Upload className="h-4 w-4" aria-hidden />
        {uploading ? "Uploading…" : "Upload Documents"}
      </Button>
      {error && <p className="mt-2 text-sm text-danger-500">{error}</p>}
    </div>
  );
}
