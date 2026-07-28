// ShareHistoryModal.tsx
import { useState } from "react";
import { X, Check, Copy, Loader2 } from "lucide-react";
import { api } from "@/lib/api/client";
import { useAuthStore } from "@/lib/store/auth.store";

interface DocumentOption {
  id: string;
  title: string;
}

interface Props {
  documents: DocumentOption[]; // pásale la lista ya cargada en DashboardPage (documentos)
  onClose: () => void;
}

export default function ShareHistoryModal({ documents, onClose }: Props) {
  const user = useAuthStore((s) => s.user);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [professionalName, setProfessionalName] = useState("");
  const [professionalRut, setProfessionalRut] = useState("");
  const [expiresInHours, setExpiresInHours] = useState(24);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [shareResult, setShareResult] = useState<{ share_url: string; expires_at: string } | null>(null);
  const [copied, setCopied] = useState(false);

  const toggleDocument = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    );
  };

    const handleSubmit = async () => {
        setError(null);

        if (selectedIds.length === 0) {
        setError("Selecciona al menos un documento para compartir.");
        return;
        }
        if (!professionalName.trim() || !professionalRut.trim()) {
        setError("Ingresa el nombre y RUT del profesional o clínica.");
        return;
        }

        setLoading(true);
        try {
        const res = await api.post(`/sharing/?email=${user?.email}`, {
            document_ids: selectedIds,
            professional_name: professionalName,
            professional_rut: professionalRut,
            expires_in_hours: expiresInHours,
        });
        setShareResult(res.data.share);
        } catch (err: any) {
        const errors = err?.response?.data?.errors;
        if (errors && typeof errors === "object") {
            const firstError = Object.values(errors)[0];
            setError(Array.isArray(firstError) ? firstError[0] : String(firstError));
        } else {
            setError(err?.response?.data?.message ?? "No se pudo crear el enlace para compartir.");
        }
        } finally {
        setLoading(false);
        }
    };

  const handleCopy = async () => {
    if (!shareResult) return;
    await navigator.clipboard.writeText(shareResult.share_url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Compartir historial</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={20} />
          </button>
        </div>

        {!shareResult ? (
          <>
            <p className="text-xs font-medium text-gray-600 mb-2">
              Selecciona los documentos que quieres compartir
            </p>
            <div className="max-h-40 overflow-y-auto border border-gray-100 rounded-lg divide-y divide-gray-50 mb-4">
              {documents.length === 0 ? (
                <p className="text-xs text-gray-400 text-center py-4">No hay documentos disponibles.</p>
              ) : (
                documents.map((doc) => (
                  <label
                    key={doc.id}
                    className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 cursor-pointer hover:bg-gray-50">
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(doc.id)}
                      onChange={() => toggleDocument(doc.id)}
                      className="w-4 h-4 accent-primary-mid"
                    />
                    {doc.title}
                  </label>
                ))
              )}
            </div>

            <div className="grid grid-cols-1 gap-3 mb-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Nombre del profesional o clínica</label>
                <input
                  value={professionalName}
                  onChange={(e) => setProfessionalName(e.target.value)}
                  placeholder="Ej: Dra. Camila Flores"
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">RUT del profesional</label>
                <input
                  value={professionalRut}
                  onChange={(e) => setProfessionalRut(e.target.value)}
                  placeholder="12345678-9"
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid"
                />
              </div>
                <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Vigencia del enlace</label>
                <select
                    value={expiresInHours}
                    onChange={(e) => setExpiresInHours(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid">
                    <option value={24}>24 horas</option>
                    <option value={48}>48 horas</option>
                    <option value={72}>72 horas</option>
                    <option value={168}>7 días</option>
                </select>
                </div>
            </div>
            

            {error && <p className="text-xs text-red-500 mb-3">{error}</p>}

            <div className="flex gap-3">
              <button
                onClick={onClose}
                className="flex-1 py-2 rounded-lg border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                Cancelar
              </button>
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="flex-1 py-2 rounded-lg bg-primary-mid text-white text-sm font-medium hover:bg-primary-dark transition-colors disabled:opacity-60 flex items-center justify-center gap-2">
                {loading ? <Loader2 size={15} className="animate-spin" /> : null}
                {loading ? "Creando..." : "Crear enlace"}
              </button>
            </div>
          </>
        ) : (
          <div>
            <p className="text-sm text-gray-700 mb-3">
              Enlace creado. Válido hasta{" "}
              <span className="font-medium">
                {new Date(shareResult.expires_at).toLocaleString("es-CL")}
              </span>
              .
            </p>
            <div className="flex items-center gap-2 border border-gray-200 rounded-lg px-3 py-2 mb-4">
              <input
                readOnly
                value={shareResult.share_url}
                className="flex-1 text-xs text-gray-600 outline-none bg-transparent truncate"
              />
              <button onClick={handleCopy} className="text-primary-mid hover:text-primary-dark flex-shrink-0">
                {copied ? <Check size={16} /> : <Copy size={16} />}
              </button>
            </div>
            <button
              onClick={onClose}
              className="w-full py-2 rounded-lg bg-primary-mid text-white text-sm font-medium hover:bg-primary-dark transition-colors">
              Listo
            </button>
          </div>
        )}
      </div>
    </div>
  );
}