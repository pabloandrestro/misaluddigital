import { useState } from "react";
import { X, Plus, Trash2 } from "lucide-react";
import { api } from "@/lib/api/client";
import { useAuthStore } from "@/lib/store/auth.store";

interface Medication {
  id?: string;
  name: string;
  dose?: string;
  frequency?: string;
  start_date?: string | null;
  end_date?: string | null;
  notes?: string;
  active?: boolean;
}

interface MedicalHistoryEntry {
  title: string;
  type?: string;
  description?: string;
}

interface MedicalProfile {
  first_name: string;
  last_name: string;
  birthdate: string;
  genre: string;
  blood_type: string;
  weight: number;
  height: number;
  allergies: string[];
  chronic_conditions: string[];
  phone_number: string;
  address: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  emergency_contact_email: string;
  emergency_contact_relationship: string;
  current_medications: Medication[];
  recent_medical_history: MedicalHistoryEntry[];
}

interface Props {
  profile: MedicalProfile;
  onClose: () => void;
  onSuccess: (updated: MedicalProfile) => void;
}

const BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];
const GENRES = ["Masculino", "Femenino", "No binario", "Otro"];

const EMPTY_MEDICATION: Medication = {
  name: "",
  dose: "",
  frequency: "",
  start_date: null,
  end_date: null,
  notes: "",
  active: true,
};

const EMPTY_HISTORY_ENTRY: MedicalHistoryEntry = {
  title: "",
  type: "",
  description: "",
};

const TABS = [
  { id: "personal", label: "Personal" },
  { id: "salud", label: "Salud" },
  { id: "emergencia", label: "Emergencia" },
  { id: "medicamentos", label: "Medicamentos" },
  { id: "historial", label: "Historial" },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function EditProfileModal({ profile, onClose, onSuccess }: Props) {
  const user = useAuthStore((s) => s.user);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>("personal");
  const [form, setForm] = useState<MedicalProfile>({
    ...profile,
    current_medications: profile.current_medications ?? [],
    recent_medical_history: profile.recent_medical_history ?? [],
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    if (name === "allergies" || name === "chronic_conditions") {
      setForm((f) => ({
        ...f,
        [name]: value.split(",").map((v) => v.trim()).filter((v) => v !== ""),
      }));
    } else {
      setForm((f) => ({ ...f, [name]: name === "weight" || name === "height" ? Number(value) : value }));
    }
  };

  // Maneja cambios dentro de un medicamento especifico por indice
  const handleMedicationChange = (
    index: number,
    field: keyof Medication,
    value: string | boolean
  ) => {
    setForm((f) => {
      const updated = [...f.current_medications];
      updated[index] = { ...updated[index], [field]: value };
      return { ...f, current_medications: updated };
    });
  };

  const addMedication = () => {
    setForm((f) => ({
      ...f,
      current_medications: [...f.current_medications, { ...EMPTY_MEDICATION }],
    }));
  };

  const removeMedication = (index: number) => {
    setForm((f) => ({
      ...f,
      current_medications: f.current_medications.filter((_, i) => i !== index),
    }));
  };

  // Maneja cambios dentro de una entrada especifica del historial clinico
  const handleHistoryChange = (
    index: number,
    field: keyof MedicalHistoryEntry,
    value: string
  ) => {
    setForm((f) => {
      const updated = [...f.recent_medical_history];
      updated[index] = { ...updated[index], [field]: value };
      return { ...f, recent_medical_history: updated };
    });
  };

  const addHistoryEntry = () => {
    setForm((f) => ({
      ...f,
      recent_medical_history: [...f.recent_medical_history, { ...EMPTY_HISTORY_ENTRY }],
    }));
  };

  const removeHistoryEntry = (index: number) => {
    setForm((f) => ({
      ...f,
      recent_medical_history: f.recent_medical_history.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      // limpia medicamentos sin nombre antes de enviar, ya que el backend lo exige
      const cleanedMedications = form.current_medications.filter(
        (m) => m.name && m.name.trim() !== ""
      );
      // limpia entradas de historial sin titulo, ya que el backend lo exige
      const cleanedHistory = form.recent_medical_history.filter(
        (h) => h.title && h.title.trim() !== ""
      );
      await api.patch(`/auth/profile/`, {
        ...form,
        current_medications: cleanedMedications,
        recent_medical_history: cleanedHistory,
        email: user?.email,
      });
      onSuccess({ ...form, current_medications: cleanedMedications, recent_medical_history: cleanedHistory });
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.message ?? "Error al actualizar el perfil.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 overflow-y-auto py-6">
      <div className="w-full max-w-lg bg-white rounded-xl shadow-xl p-6 flex flex-col max-h-[85vh]">

        {/* Header */}
        <div className="flex items-center justify-between mb-3 flex-shrink-0">
          <h2 className="text-lg font-semibold text-gray-900">Editar perfil</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={20} />
          </button>
        </div>

        {/* Pestañas */}
        <div className="flex gap-1 border-b border-gray-200 mb-4 flex-shrink-0 overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-2 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "border-primary-mid text-primary-mid"
                  : "border-transparent text-gray-400 hover:text-gray-600"
              }`}>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Contenido con scroll */}
        <div className="space-y-3 overflow-y-auto flex-1 pr-1">

          {/* Pestaña: Personal */}
          {activeTab === "personal" && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Nombre</label>
                  <input name="first_name" value={form.first_name} onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Apellido</label>
                  <input name="last_name" value={form.last_name} onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Fecha de nacimiento</label>
                  <input name="birthdate" type="date" value={form.birthdate} onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Sexo</label>
                  <select name="genre" value={form.genre} onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid">
                    <option value="">Seleccionar...</option>
                    {GENRES.map((g) => <option key={g} value={g}>{g}</option>)}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Grupo sanguíneo</label>
                  <select name="blood_type" value={form.blood_type} onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid">
                    <option value="">Seleccionar...</option>
                    {BLOOD_TYPES.map((b) => <option key={b} value={b}>{b}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Peso (kg)</label>
                  <input name="weight" type="number" value={form.weight} onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Altura (cm)</label>
                  <input name="height" type="number" value={form.height} onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Teléfono</label>
                  <input name="phone_number" value={form.phone_number} onChange={handleChange}
                    placeholder="+56912345678"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Dirección</label>
                  <input name="address" value={form.address} onChange={handleChange}
                    placeholder="Calle 123, Comuna"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                </div>
              </div>
            </>
          )}

          {/* Pestaña: Salud */}
          {activeTab === "salud" && (
            <div className="grid grid-cols-1 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Alergias</label>
                <input name="allergies" value={form.allergies.join(", ")} onChange={handleChange}
                  placeholder="Ej: Penicilina, Polen"
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                <p className="text-xs text-gray-400 mt-1">Separadas por coma</p>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Condiciones crónicas</label>
                <input name="chronic_conditions" value={form.chronic_conditions.join(", ")} onChange={handleChange}
                  placeholder="Ej: Hipertensión, Diabetes"
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                <p className="text-xs text-gray-400 mt-1">Separadas por coma</p>
              </div>
            </div>
          )}

          {/* Pestaña: Emergencia */}
          {activeTab === "emergencia" && (
            <div>
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Nombre</label>
                  <input name="emergency_contact_name" value={form.emergency_contact_name} onChange={handleChange}
                    placeholder="Nombre del contacto"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Teléfono</label>
                  <input name="emergency_contact_phone" value={form.emergency_contact_phone} onChange={handleChange}
                    placeholder="+56912345678"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Correo</label>
                  <input name="emergency_contact_email" type="email" value={form.emergency_contact_email} onChange={handleChange}
                    placeholder="correo@ejemplo.cl"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Relación</label>
                  <input name="emergency_contact_relationship" value={form.emergency_contact_relationship} onChange={handleChange}
                    placeholder="Ej: Madre, Cónyuge"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                </div>
              </div>
            </div>
          )}

          {/* Pestaña: Medicamentos */}
          {activeTab === "medicamentos" && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-gray-700">Medicamentos actuales</p>
                <button
                  type="button"
                  onClick={addMedication}
                  className="flex items-center gap-1 text-xs text-primary-mid hover:underline">
                  <Plus size={12} strokeWidth={2.5} /> Agregar
                </button>
              </div>

              {form.current_medications.length === 0 && (
                <p className="text-xs text-gray-400 mb-2">Sin medicamentos registrados</p>
              )}

              <div className="space-y-3">
                {form.current_medications.map((med, i) => (
                  <div key={i} className="border border-gray-200 rounded-lg p-3 relative">
                    <button
                      type="button"
                      onClick={() => removeMedication(i)}
                      className="absolute top-2 right-2 text-gray-300 hover:text-red-500">
                      <Trash2 size={14} />
                    </button>
                    <div className="grid grid-cols-2 gap-2 mb-2 pr-6">
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Nombre *</label>
                        <input
                          value={med.name}
                          onChange={(e) => handleMedicationChange(i, "name", e.target.value)}
                          placeholder="Ej: Paracetamol"
                          className="w-full px-2 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Dosis</label>
                        <input
                          value={med.dose ?? ""}
                          onChange={(e) => handleMedicationChange(i, "dose", e.target.value)}
                          placeholder="Ej: 500mg"
                          className="w-full px-2 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 mb-2">
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Frecuencia</label>
                        <input
                          value={med.frequency ?? ""}
                          onChange={(e) => handleMedicationChange(i, "frequency", e.target.value)}
                          placeholder="Ej: Cada 8 horas"
                          className="w-full px-2 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                      </div>
                      <div className="flex items-end gap-2 pb-1.5">
                        <input
                          type="checkbox"
                          checked={med.active ?? true}
                          onChange={(e) => handleMedicationChange(i, "active", e.target.checked)}
                          className="w-4 h-4" />
                        <label className="text-xs text-gray-600">En uso actualmente</label>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 mb-2">
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Fecha inicio</label>
                        <input
                          type="date"
                          value={med.start_date ?? ""}
                          onChange={(e) => handleMedicationChange(i, "start_date", e.target.value)}
                          className="w-full px-2 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Fecha fin</label>
                        <input
                          type="date"
                          value={med.end_date ?? ""}
                          onChange={(e) => handleMedicationChange(i, "end_date", e.target.value)}
                          className="w-full px-2 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Notas</label>
                      <input
                        value={med.notes ?? ""}
                        onChange={(e) => handleMedicationChange(i, "notes", e.target.value)}
                        placeholder="Observaciones adicionales"
                        className="w-full px-2 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Pestaña: Historial */}
          {activeTab === "historial" && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-gray-700">Historial clínico reciente</p>
                <button
                  type="button"
                  onClick={addHistoryEntry}
                  className="flex items-center gap-1 text-xs text-primary-mid hover:underline">
                  <Plus size={12} strokeWidth={2.5} /> Agregar
                </button>
              </div>

              {form.recent_medical_history.length === 0 && (
                <p className="text-xs text-gray-400 mb-2">Sin historial registrado</p>
              )}

              <div className="space-y-3">
                {form.recent_medical_history.map((entry, i) => (
                  <div key={i} className="border border-gray-200 rounded-lg p-3 relative">
                    <button
                      type="button"
                      onClick={() => removeHistoryEntry(i)}
                      className="absolute top-2 right-2 text-gray-300 hover:text-red-500">
                      <Trash2 size={14} />
                    </button>
                    <div className="grid grid-cols-2 gap-2 mb-2 pr-6">
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Título *</label>
                        <input
                          value={entry.title}
                          onChange={(e) => handleHistoryChange(i, "title", e.target.value)}
                          placeholder="Ej: Cirugía de apéndice"
                          className="w-full px-2 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Tipo</label>
                        <input
                          value={entry.type ?? ""}
                          onChange={(e) => handleHistoryChange(i, "type", e.target.value)}
                          placeholder="Ej: Cirugía, Consulta"
                          className="w-full px-2 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Descripción</label>
                      <input
                        value={entry.description ?? ""}
                        onChange={(e) => handleHistoryChange(i, "description", e.target.value)}
                        placeholder="Detalle adicional"
                        className="w-full px-2 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {error && <p className="text-xs text-red-500">{error}</p>}
        </div>

        {/* Botones */}
        <div className="flex gap-3 mt-4 pt-3 border-t border-gray-100 flex-shrink-0">
          <button onClick={onClose}
            className="flex-1 py-2 rounded-lg border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
            Cancelar
          </button>
          <button onClick={handleSubmit} disabled={loading}
            className="flex-1 py-2 rounded-lg bg-primary-mid text-white text-sm font-medium hover:bg-primary-dark transition-colors disabled:opacity-60">
            {loading ? "Guardando..." : "Guardar cambios"}
          </button>
        </div>
      </div>
    </div>
  );
}
