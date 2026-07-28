import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { FileText, Clock, AlertCircle } from "lucide-react";
import { api } from "@/lib/api/client";
import logoSaludaldia from "@/assets/logo/logo-saludaldia.png";
import textoSaludaldia from "@/assets/logo/texto.png";

interface SharedDocument {
  id: string;
  title: string;
  mime_type: string | null;
  view_url: string;
  expires_in: number;
}

interface ShareData {
  professional_name: string;
  professional_rut: string;
  expires_at: string;
  documents: SharedDocument[];
}

export default function SharePage() {
  const { token } = useParams<{ token: string }>();
  const [data, setData] = useState<ShareData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;

    const fetchShare = async () => {
      try {
        const res = await api.get(`/sharing/${token}/`);
        setData(res.data.share);
      } catch (err: any) {
        setError(
          err?.response?.data?.message ??
            "Este enlace no es válido o ya no está disponible."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchShare();
  }, [token]);

  return (
    <div className="min-h-screen bg-surface-light p-6">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center gap-2 mb-6">
          <img src={logoSaludaldia} alt="Saludaldia" className="w-4 h-6 object-contain" />
          <img src={textoSaludaldia} alt="Saludaldia" className="h-4 object-contain" />
          <span className="text-sm text-gray-500">— Acceso médico</span>
        </div>

        {loading && (
          <p className="text-sm text-gray-500">Cargando documentos compartidos...</p>
        )}

        {!loading && (error || !data) && (
          <div className="bg-white rounded-xl shadow-md p-6 text-center">
            <AlertCircle size={32} className="text-red-400 mx-auto mb-3" />
            <p className="text-sm font-medium text-gray-900 mb-1">Enlace no disponible</p>
            <p className="text-xs text-gray-500">{error}</p>
          </div>
        )}

        {!loading && data && (
          <>
            <div className="bg-white rounded-xl shadow-md p-6 mb-4">
              <p className="text-sm text-gray-700 mb-1">
                Acceso otorgado a <span className="font-medium">{data.professional_name}</span>{" "}
                (RUT {data.professional_rut})
              </p>
              <div className="flex items-center gap-2 text-xs text-gray-400 mt-2">
                <Clock size={13} />
                Este enlace expira el {new Date(data.expires_at).toLocaleString("es-CL")}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md divide-y divide-gray-50">
              {data.documents.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-8">
                  No hay documentos disponibles en este enlace.
                </p>
              ) : (
                data.documents.map((doc) => (
                  <div key={doc.id} className="flex items-center gap-3 px-5 py-4">
                    <FileText size={20} className="text-brand-700 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">{doc.title}</p>
                      <p className="text-xs text-gray-400">{doc.mime_type ?? "Archivo"}</p>
                    </div>
                    <a
                      href={doc.view_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-medium text-brand-700 hover:underline flex-shrink-0">
                      Ver documento
                    </a>
                  </div>
                ))
              )}
            </div>

            <p className="text-center text-xs text-gray-400 mt-6">
              Este enlace expira automáticamente. Los archivos están protegidos por acceso temporal firmado.
            </p>
          </>
        )}
      </div>
    </div>
  );
}