import { useRef, useState } from "react";
import { X, Upload, Trash2, Camera } from "lucide-react";
import { api } from "@/lib/api/client";
import { useAuthStore } from "@/lib/store/auth.store";

interface Props {
  currentImageUrl?: string;
  onClose: () => void;
  onSuccess: (newImageUrl: string) => void;
  onDeleted: () => void;
}

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_SIZE = 5 * 1024 * 1024; // 5 MB
const MIN_DIMENSION = 300;
const MAX_DIMENSION = 1024;

export default function ProfileImageModal({ currentImageUrl, onClose, onSuccess, onDeleted }: Props) {
  const user = useAuthStore((s) => s.user);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(currentImageUrl ?? null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Valida tipo, tamaño y resolucion en el navegador antes de subir
  const validateAndSetFile = (file: File) => {
    setError(null);

    if (!ALLOWED_TYPES.includes(file.type)) {
      setError("Tipo de imagen no permitido. Use JPG, PNG o WEBP.");
      return;
    }

    if (file.size > MAX_SIZE) {
      setError("La imagen de perfil no puede superar los 5 MB.");
      return;
    }

    const img = new Image();
    const objectUrl = URL.createObjectURL(file);
    img.onload = () => {
      if (img.width < MIN_DIMENSION || img.height < MIN_DIMENSION) {
        setError(`La imagen debe tener al menos ${MIN_DIMENSION}x${MIN_DIMENSION} píxeles.`);
        URL.revokeObjectURL(objectUrl);
        return;
      }
      if (img.width > MAX_DIMENSION || img.height > MAX_DIMENSION) {
        setError(`La imagen no debe superar ${MAX_DIMENSION}x${MAX_DIMENSION} píxeles.`);
        URL.revokeObjectURL(objectUrl);
        return;
      }
      setSelectedFile(file);
      setPreview(objectUrl);
    };
    img.onerror = () => {
      setError("El archivo no es una imagen válida.");
      URL.revokeObjectURL(objectUrl);
    };
    img.src = objectUrl;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) validateAndSetFile(file);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) validateAndSetFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("image", selectedFile);
      formData.append("email", user?.email ?? "");

      const res = await api.post(`/auth/profile/image/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const newUrl = res.data?.image?.profile_image_url;
      onSuccess(newUrl);
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.message ?? "Error al subir la imagen de perfil.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    setError(null);
    try {
      await api.delete(`/auth/profile/image/`, {
        data: { email: user?.email },
      });
      setPreview(null);
      setSelectedFile(null);
      onDeleted();
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.message ?? "Error al eliminar la imagen de perfil.");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-sm bg-white rounded-xl shadow-xl p-6">

        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Foto de perfil</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={20} />
          </button>
        </div>

        {/* Zona de preview / drop */}
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => fileInputRef.current?.click()}
          className="w-40 h-40 mx-auto rounded-full border-2 border-dashed border-gray-300 flex items-center justify-center overflow-hidden cursor-pointer hover:border-primary-mid transition-colors mb-4 bg-gray-50">
          {preview ? (
            <img src={preview} alt="Vista previa" className="w-full h-full object-cover" />
          ) : (
            <div className="flex flex-col items-center text-gray-400 px-2 text-center">
              <Camera size={28} strokeWidth={1.5} />
              <p className="text-xs mt-1">Arrastra o haz clic</p>
            </div>
          )}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileChange}
          className="hidden"
        />

        <p className="text-xs text-gray-400 text-center mb-3">
          JPG, PNG o WEBP · máx. 5MB · entre 300x300 y 1024x1024 px
        </p>

        {error && <p className="text-xs text-red-500 text-center mb-3">{error}</p>}

        {/* Botones */}
        <div className="flex flex-col gap-2">
          <button
            onClick={handleUpload}
            disabled={!selectedFile || loading}
            className="flex items-center justify-center gap-2 py-2 rounded-lg bg-primary-mid text-white text-sm font-medium hover:bg-primary-dark transition-colors disabled:opacity-60">
            <Upload size={14} strokeWidth={2.5} />
            {loading ? "Subiendo..." : "Subir imagen"}
          </button>

          {currentImageUrl && (
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="flex items-center justify-center gap-2 py-2 rounded-lg border border-red-200 text-red-500 text-sm font-medium hover:bg-red-50 transition-colors disabled:opacity-60">
              <Trash2 size={14} strokeWidth={2.5} />
              {deleting ? "Eliminando..." : "Eliminar foto actual"}
            </button>
          )}

          <button
            onClick={onClose}
            className="py-2 rounded-lg border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
}
