import { useEffect, useRef, useState } from "react";
import { X, Upload, FileText } from "lucide-react";
import { api } from "@/lib/api/client";
import { useAuthStore } from "@/lib/store/auth.store";

interface Category {
  id: string;
  name: string;
  slug: string;
}

interface Props {
  onClose: () => void;
  onSuccess: () => void;
}

const DOCUMENT_TYPES = [
  { label: "Exámen",      value: "exam"         },
  { label: "Receta",      value: "prescription" },
  { label: "Certificado", value: "report"       },
];

export default function UploadDocumentModal({ onClose, onSuccess }: Props) {
  const user = useAuthStore((s) => s.user);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState<string | null>(null);

  const [form, setForm] = useState({
    title:         "",
    document_type: "exam",
    category_id:   "",
    document_date: "",
    medical_center:"",
    specialty:     "",
    doctor_name:   "",
  });
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    api.get("/documents/categories/").then((res) => {
      setCategories(res.data.categories);
      if (res.data.categories.length > 0) {
        setForm((f) => ({ ...f, category_id: res.data.categories[0].id }));
      }
    });
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async () => {
    if (!file) { setError("Debes seleccionar un archivo."); return; }
    if (!form.title) { setError("El título es requerido."); return; }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      Object.entries(form).forEach(([k, v]) => formData.append(k, v));
      formData.append("file", file);

      await api.post(`/documents/?email=${user?.email}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.message ?? "Error al subir el documento.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-lg bg-white rounded-xl shadow-xl p-6">

        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold text-gray-900">Subir documento</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={20} />
          </button>
        </div>

        {/* Formulario */}
        <div className="space-y-3">

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Título</label>
            <input name="title" value={form.title} onChange={handleChange}
              placeholder="Ej: Hemograma completo"
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Tipo de documento</label>
              <select name="document_type" value={form.document_type} onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid">
                {DOCUMENT_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Categoría</label>
              <select name="category_id" value={form.category_id} onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid">
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Fecha del documento</label>
              <input name="document_date" type="date" value={form.document_date} onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Centro médico</label>
              <input name="medical_center" value={form.medical_center} onChange={handleChange}
                placeholder="Ej: Red Salud"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Especialidad</label>
              <input name="specialty" value={form.specialty} onChange={handleChange}
                placeholder="Ej: Cardiología"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Médico</label>
              <input name="doctor_name" value={form.doctor_name} onChange={handleChange}
                placeholder="Ej: Dr. Pérez"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
            </div>
          </div>

          {/* Área de archivo */}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Archivo</label>
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-gray-200 rounded-lg p-4 text-center cursor-pointer hover:border-primary-mid transition-colors"
            >
              {file ? (
                <div className="flex items-center justify-center gap-2 text-sm text-gray-700">
                  <FileText size={16} className="text-primary-mid" />
                  {file.name}
                </div>
              ) : (
                <div className="text-sm text-gray-400">
                  <Upload size={20} className="mx-auto mb-1 text-gray-300" />
                  Haz clic para seleccionar un archivo (PDF, JPG, PNG)
                </div>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </div>

          {error && <p className="text-xs text-red-500">{error}</p>}
        </div>

        {/* Botones */}
        <div className="flex gap-3 mt-5">
          <button onClick={onClose}
            className="flex-1 py-2 rounded-lg border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
            Cancelar
          </button>
          <button onClick={handleSubmit} disabled={loading}
            className="flex-1 py-2 rounded-lg bg-primary-mid text-white text-sm font-medium hover:bg-primary-dark transition-colors disabled:opacity-60">
            {loading ? "Subiendo..." : "Subir documento"}
          </button>
        </div>

      </div>
    </div>
  );
}