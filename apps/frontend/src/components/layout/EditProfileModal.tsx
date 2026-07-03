import { useState } from "react";
import { X } from "lucide-react";
import { api } from "@/lib/api/client";
import { useAuthStore } from "@/lib/store/auth.store";

interface MedicalProfile {
  first_name: string;
  last_name: string;
  birthdate: string;
  genre: string;
  blood_type: string;
  weight: number;
  height: number;
  allergies: string;
  chronic_conditions: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
}

interface Props {
  profile: MedicalProfile;
  onClose: () => void;
  onSuccess: (updated: MedicalProfile) => void;
}

const BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];
const GENRES = ["Masculino", "Femenino", "Otro"];

export default function EditProfileModal({ profile, onClose, onSuccess }: Props) {
  const user = useAuthStore((s) => s.user);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<MedicalProfile>({ ...profile });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: name === "weight" || name === "height" ? Number(value) : value }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      await api.put(`/auth/profile/`, { ...form, email: user?.email });
      onSuccess(form);
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.message ?? "Error al actualizar el perfil.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 overflow-y-auto py-6">
      <div className="w-full max-w-lg bg-white rounded-xl shadow-xl p-6">

        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold text-gray-900">Editar perfil</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={20} />
          </button>
        </div>

        <div className="space-y-3">

          {/* Nombre y apellido */}
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

          {/* Fecha y género */}
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
                {GENRES.map((g) => <option key={g} value={g}>{g}</option>)}
              </select>
            </div>
          </div>

          {/* Grupo sanguíneo, peso y altura */}
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Grupo sanguíneo</label>
              <select name="blood_type" value={form.blood_type} onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid">
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

          {/* Alergias y condiciones */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Alergias</label>
              <input name="allergies" value={form.allergies} onChange={handleChange}
                placeholder="Ej: Penicilina, Polen"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Condiciones crónicas</label>
              <input name="chronic_conditions" value={form.chronic_conditions} onChange={handleChange}
                placeholder="Ej: Hipertensión, Diabetes"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
            </div>
          </div>

          {/* Contacto de emergencia */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Contacto de emergencia</label>
              <input name="emergency_contact_name" value={form.emergency_contact_name} onChange={handleChange}
                placeholder="Nombre del contacto"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Teléfono de emergencia</label>
              <input name="emergency_contact_phone" value={form.emergency_contact_phone} onChange={handleChange}
                placeholder="+56912345678"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
            </div>
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
            {loading ? "Guardando..." : "Guardar cambios"}
          </button>
        </div>
      </div>
    </div>
  );
}