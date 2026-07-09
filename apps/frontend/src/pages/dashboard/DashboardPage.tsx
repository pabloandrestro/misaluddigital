import { useAuthStore } from "@/lib/store/auth.store";
import { Share2, Upload, Lightbulb, ShieldCheck, Download, Share2 as ShareIcon, Trash2, Eye, X } from "lucide-react";
import { useState, useEffect } from "react";
import robotImg from "@/assets/img/robot.png";
import fondoSeguridadImg from "@/assets/img/fondo-seguridad.png";
import iconoDocumentos from "@/assets/img/icono-documentos.png";
import iconoExamenes from "@/assets/img/icono-examenes.png";
import iconoLicencias from "@/assets/img/icono-licencias.png";
import iconoRecetas from "@/assets/img/icono-recetas.png";
import UploadDocumentModal from "@/components/layout/UploadDocumentModal";
import { api } from "@/lib/api/client";

// Documento tal como lo devuelve DocumentSerializer: las claves son las de la
// izquierda de cada CharField(source=...), no el nombre de columna del modelo.
interface Document {
  id: string;
  title: string;
  document_type: string;
  document_date: string | null;
  medical_center: string | null;
  doctor_name: string | null;
  file_url: string | null;
  mime_type: string | null;
}

// Traduce el valor real de doc_type (backend) a una etiqueta en español
const DOC_TYPE_LABELS: Record<string, string> = {
  exam: "Examen",
  prescription: "Receta",
  sick_leave: "Licencia",
  report: "Certificado",
  vaccine: "Vacuna",
  other: "Otro",
};

// Pestañas de filtro: label visible + valor real que se compara contra document_type
const CATEGORIAS: { label: string; value: string | null }[] = [
  { label: "Todos", value: null },
  { label: "Examen", value: "exam" },
  { label: "Receta", value: "prescription" },
  { label: "Licencia", value: "sick_leave" },
];

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  const [documentos, setDocumentos] = useState<Document[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);

  const fetchDocuments = async () => {
    try {
      const res = await api.get(`/documents/?email=${user?.email}`);
      setDocumentos(res.data.documents);
    } catch (err) {
      console.error("Error al cargar documentos:", err);
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    if (user?.email) fetchDocuments();
  }, [user?.email]);

  const STATS = [
    { label: "Exámenes",   value: documentos.filter(d => d.document_type === "exam").length,        icono: iconoExamenes,  border: "border-b-categoria-examenes"  },
    { label: "Recetas",    value: documentos.filter(d => d.document_type === "prescription").length, icono: iconoRecetas,   border: "border-b-categoria-recetas"   },
    { label: "Licencias",  value: documentos.filter(d => d.document_type === "sick_leave").length,   icono: iconoLicencias, border: "border-b-categoria-licencias" },
    { label: "Documentos", value: documentos.length,                                                  icono: iconoDocumentos,border: "border-b-categoria-documentos"},
  ];

  const handleDelete = async (id: string) => {
    if (!confirm("¿Estás segura de que deseas eliminar este documento?")) return;
    try {
      await api.delete(`/documents/${id}/?email=${user?.email}`);
      setDocumentos((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      console.error("Error al eliminar documento:", err);
      alert("No se pudo eliminar el documento.");
    }
  };

  // Descarga el archivo forzando el nombre del documento en vez de abrir una pestaña nueva
  const handleDownload = async (doc: Document) => {
    if (!doc.file_url) {
      alert("Este documento no tiene un archivo asociado.");
      return;
    }
    try {
      const response = await fetch(doc.file_url);
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);
      const extension = doc.mime_type?.split("/")[1] ?? "";
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = extension ? `${doc.title}.${extension}` : doc.title;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(blobUrl);
    } catch (err) {
      console.error("Error al descargar el documento:", err);
      // Si falla la descarga forzada (ej. por CORS), al menos abre el archivo en una pestaña nueva
      window.open(doc.file_url, "_blank");
    }
  };

  // Comparte el link del documento usando la API nativa del navegador, o lo copia al portapapeles
  const handleShare = async (doc: Document) => {
    if (!doc.file_url) {
      alert("Este documento no tiene un archivo asociado.");
      return;
    }
    if (navigator.share) {
      try {
        await navigator.share({ title: doc.title, url: doc.file_url });
      } catch (err) {
        // el usuario cancelo el share, no hacemos nada
      }
    } else {
      try {
        await navigator.clipboard.writeText(doc.file_url);
        alert("Enlace copiado al portapapeles.");
      } catch (err) {
        console.error("Error al copiar el enlace:", err);
        alert("No se pudo copiar el enlace.");
      }
    }
  };

  const documentosFiltrados = documentos.filter(
    (doc) => activeTab === null || doc.document_type === activeTab
  );

  return (
    <div className="p-4 md:p-6">

      {/* Bienvenida + botones */}
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl md:text-2xl font-semibold text-gray-900">
            Bienvenido de nuevo,{" "}
            <span className="text-primary-mid">{user?.name || "Usuario"}</span>
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Aquí está el resumen de tu actividad médica reciente.
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <button className="flex items-center justify-center gap-2 px-4 py-2 rounded-full border border-primary-mid text-primary-mid text-sm hover:bg-primary-light transition-colors">
            <Share2 size={15} />
            Compartir historial
          </button>
          <button
            onClick={() => setShowUpload(true)}
            className="flex items-center justify-center gap-2 px-4 py-2 rounded-full bg-primary-mid text-white text-sm hover:bg-primary-dark transition-colors">
            <Upload size={15} />
            Subir documento
          </button>
        </div>
      </div>

      {/* Layout responsivo */}
      <div className="flex flex-col lg:flex-row gap-6 items-start">

        {/* COLUMNA IZQUIERDA */}
        <div className="flex-1 min-w-0 w-full">

          {/* Tarjetas de resumen */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {STATS.map(({ label, value, icono, border }) => (
              <div key={label} className={`bg-white rounded-xl shadow-md p-4 flex flex-col items-center gap-2 border border-gray-100 border-b-4 ${border}`}>
                <img src={icono} alt={label} className="w-10 h-10 md:w-12 md:h-12 object-contain" />
                <p className="text-xl md:text-2xl font-semibold text-gray-900">{value}</p>
                <p className="text-xs md:text-sm text-gray-400 text-center">{label}</p>
              </div>
            ))}
          </div>

          {/* Tabla de documentos */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4">

            {/* Tabs */}
            <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
              {CATEGORIAS.map((tab) => (
                <button
                  key={tab.label}
                  onClick={() => setActiveTab(tab.value)}
                  className={`px-4 py-1.5 rounded-full text-sm transition-colors flex-shrink-0 ${
                    activeTab === tab.value
                      ? "bg-primary-mid text-white font-medium"
                      : "text-gray-500 hover:bg-gray-100"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Filas */}
            <div className="divide-y divide-gray-50">
              {loadingDocs ? (
                <p className="text-sm text-gray-400 text-center py-4">Cargando documentos...</p>
              ) : documentos.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-4">No hay documentos registrados.</p>
              ) : documentosFiltrados.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-4">No hay documentos en esta categoría.</p>
              ) : (
                documentosFiltrados.map((doc) => (
                    <div key={doc.id} className="flex items-center gap-2 md:gap-4 py-3">
                      <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center text-sm flex-shrink-0">
                        📄
                      </div>
                      <p className="flex-1 min-w-0 text-sm text-gray-700 font-medium truncate">{doc.title}</p>
                      <span className="hidden sm:inline px-3 py-0.5 rounded-full text-xs font-medium flex-shrink-0 bg-gray-100 text-gray-600">
                        {DOC_TYPE_LABELS[doc.document_type] ?? doc.document_type}
                      </span>
                      <p className="hidden md:block text-xs text-gray-400 w-24 text-right flex-shrink-0">
                        {doc.document_date ? new Date(doc.document_date + "T00:00:00").toLocaleDateString("es-CL") : "—"}
                      </p>
                      <div className="flex gap-2 md:gap-3 text-gray-400 flex-shrink-0">
                        <button onClick={() => handleDownload(doc)} className="hover:text-primary-mid transition-colors"><Download size={15} /></button>
                        <button onClick={() => handleShare(doc)} className="hover:text-primary-mid transition-colors"><ShareIcon size={15} /></button>
                        <button
                          onClick={() => setSelectedDoc(doc)}
                          className="hover:text-primary-mid transition-colors">
                          <Eye size={15} />
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id)}
                          className="hover:text-red-400 transition-colors">
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </div>
                  ))
              )}
            </div>

            {/* Ver historial completo */}
            <div className="text-center mt-4">
              <button className="text-sm text-primary-mid hover:underline">
                Ver historial completo
              </button>
            </div>
          </div>
        </div>

        {/* COLUMNA DERECHA */}
        <div className="w-full lg:w-64 flex-shrink-0 flex flex-col gap-4">

          {/* Consejo del día */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4">
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb size={18} className="text-yellow-400" />
              <p className="text-sm font-medium text-gray-700">Consejo de hoy</p>
            </div>
            <p className="text-sm text-gray-500 text-center leading-relaxed mb-4">
              Sube tus exámenes apenas los recibas para mantener tu historial actualizado.
            </p>
            <div className="flex justify-center">
              <img src={robotImg} alt="Robot IA" className="w-24 h-24 object-contain" />
            </div>
          </div>

          {/* Protege tu información */}
          <div className="rounded-xl overflow-hidden text-white relative min-h-64 lg:min-h-80" style={{ backgroundImage: `url(${fondoSeguridadImg})`, backgroundSize: "cover", backgroundPosition: "center" }}>
            <div className="p-4 flex flex-col gap-3">
              <div className="flex items-center gap-2">
                <ShieldCheck size={16} className="text-white" />
                <p className="text-sm font-medium text-white">Protege tu información</p>
              </div>
              <p className="text-xs text-white/90 leading-relaxed">
                Tu historial médico está cifrado y protegido. Solo tú decides quién puede verlo.
              </p>
            </div>
            <div className="absolute bottom-4 left-4 right-4">
              <button className="w-full py-2.5 rounded-lg bg-primary-mid text-white text-xs font-medium hover:bg-primary-accent transition-colors">
                Ver más
              </button>
            </div>
          </div>
        </div>

      </div>

      {/* Modal subir documento */}
      {showUpload && (
        <UploadDocumentModal
          onClose={() => setShowUpload(false)}
          onSuccess={() => {
            setShowUpload(false);
            fetchDocuments();
          }}
        />
      )}

      {/* Modal ver documento */}
      {selectedDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <div className="w-full max-w-md bg-white rounded-xl shadow-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">{selectedDoc.title}</h2>
              <button onClick={() => setSelectedDoc(null)} className="text-gray-400 hover:text-gray-600">
                <X size={20} />
              </button>
            </div>
            <dl className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <dt className="text-xs text-gray-400">Tipo</dt>
                <dd className="font-medium text-gray-900">
                  {DOC_TYPE_LABELS[selectedDoc.document_type] ?? selectedDoc.document_type}
                </dd>
              </div>
              <div>
                <dt className="text-xs text-gray-400">Fecha</dt>
                <dd className="font-medium text-gray-900">
                  {selectedDoc.document_date
                    ? new Date(selectedDoc.document_date + "T00:00:00").toLocaleDateString("es-CL")
                    : "—"}
                </dd>
              </div>
              <div>
                <dt className="text-xs text-gray-400">Centro médico</dt>
                <dd className="font-medium text-gray-900">{selectedDoc.medical_center || "—"}</dd>
              </div>
              <div>
                <dt className="text-xs text-gray-400">Médico</dt>
                <dd className="font-medium text-gray-900">{selectedDoc.doctor_name || "—"}</dd>
              </div>
              <div>
                <dt className="text-xs text-gray-400">Tipo de archivo</dt>
                <dd className="font-medium text-gray-900">{selectedDoc.mime_type || "—"}</dd>
              </div>
            </dl>
            <div className="flex gap-3 mt-5">
              <button
                onClick={() => setSelectedDoc(null)}
                className="flex-1 py-2 rounded-lg border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                Cerrar
              </button>
              {selectedDoc.file_url && (
                <a href={selectedDoc.file_url} target="_blank" rel="noreferrer"
                  className="flex-1 py-2 rounded-lg bg-primary-mid text-white text-sm font-medium text-center hover:bg-primary-dark transition-colors">
                  Ver archivo
                </a>
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
