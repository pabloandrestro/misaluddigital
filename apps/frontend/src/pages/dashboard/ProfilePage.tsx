import { useEffect, useState } from "react";
import { useAuthStore } from "@/lib/store/auth.store";
import { api } from "@/lib/api/client";
import { Pencil, Calendar, User, Droplet, Weight, Ruler, Phone, Activity, Mail, MapPin, Heart, Clock } from "lucide-react";

interface MedicalProfile {
  first_name: string;
  last_name: string;
  birthdate: string;
  genre: string;
  blood_type: string;
  weight: number;
  height: number;
  profile_image: string;
  allergies: string;
  chronic_conditions: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
}

function calcularEdad(birthdate: string): number {
  const hoy = new Date();
  const nacimiento = new Date(birthdate + "T00:00:00");
  let edad = hoy.getFullYear() - nacimiento.getFullYear();
  const mes = hoy.getMonth() - nacimiento.getMonth();
  if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) edad--;
  return edad;
}

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user);
  const [profile, setProfile] = useState<MedicalProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get(`/auth/profile/?email=${user?.email}`);
        setProfile(res.data.user);
      } catch (err) {
        console.error("Error al cargar perfil:", err);
      } finally {
        setLoading(false);
      }
    };
    if (user?.email) fetchProfile();
  }, [user?.email]);

  if (loading) return <div className="p-4 text-gray-400 text-sm">Cargando perfil...</div>;

  return (
    <div className="p-4 md:p-6">

      {/* Header */}
      <div className="flex items-start justify-between mb-6 gap-4">
        <div>
          <h1 className="text-xl md:text-2xl font-semibold text-gray-900">Mi perfil</h1>
          <p className="text-sm text-gray-400 mt-1">Gestiona tu información personal y de salud.</p>
        </div>
        <button className="flex items-center gap-2 px-3 md:px-4 py-2 rounded-lg border border-primary-mid text-primary-mid text-sm hover:bg-primary-light transition-colors flex-shrink-0">
          <Pencil size={14} strokeWidth={2.5}/>
          <span className="hidden sm:inline">Editar perfil</span>
        </button>
      </div>

      {/* Tarjeta principal */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4 md:p-6 mb-4">
        <div className="flex flex-col md:flex-row gap-6">

          {/* Avatar + nombre + contacto */}
          <div className="flex items-start gap-4 flex-1 md:border-r md:border-gray-300 md:pr-6">
            <div className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-primary-mid flex items-center justify-center text-white text-xl md:text-2xl font-semibold flex-shrink-0">
              {profile?.first_name?.[0]}{profile?.last_name?.[0]}
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-lg md:text-xl font-semibold text-gray-900 mb-2 truncate">
                {profile?.first_name} {profile?.last_name}
              </h2>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <div className="w-7 h-7 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0">
                    <Mail size={14} strokeWidth={2.5} className="text-blue-600" />
                  </div>
                  <span className="truncate">{user?.email || "—"}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <div className="w-7 h-7 rounded-full bg-green-50 flex items-center justify-center flex-shrink-0">
                    <Phone size={14} strokeWidth={2.5} className="text-green-600" />
                  </div>
                  <span className="text-gray-400">No registrado</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <div className="w-7 h-7 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0">
                    <MapPin size={14} strokeWidth={2.5} className="text-blue-600" />
                  </div>
                  <span className="text-gray-400">No registrada</span>
                </div>
              </div>
            </div>
          </div>

          {/* Información clínica relevante */}
          <div className="flex-1 md:pl-3 border-t md:border-t-0 border-gray-200 pt-4 md:pt-0">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-full bg-primary-light flex items-center justify-center flex-shrink-0">
                <Heart size={15} strokeWidth={2.5} className="text-primary-mid" />
              </div>
              <p className="text-sm font-medium text-gray-700">Información clínica relevante</p>
            </div>
            <div className="flex flex-wrap gap-2 mb-3">
              {profile?.chronic_conditions && profile.chronic_conditions !== "Ninguna"
                ? profile.chronic_conditions.split(",").map((c, i) => (
                    <span key={i} className="px-3 py-1 bg-red-100 text-red-600 text-xs rounded-full font-medium">
                      {c.trim()}
                    </span>
                  ))
                : <p className="text-sm text-gray-400">Sin condiciones registradas</p>
              }
              {profile?.allergies && profile.allergies !== "Ninguna" &&
                profile.allergies.split(",").map((a, i) => (
                  <span key={i} className="px-3 py-1 bg-orange-100 text-orange-600 text-xs rounded-full font-medium">
                    {a.trim()}
                  </span>
                ))
              }
            </div>
          </div>

          {/* Grupo sanguíneo */}
          {profile?.blood_type && (
            <div className="flex md:flex-col items-center md:justify-center border-t md:border-t-0 md:border-l border-gray-200 pt-4 md:pt-0 md:pl-6 md:min-w-24 gap-3 md:gap-0">
              <div className="bg-red-50 rounded-xl p-3 flex flex-col items-center">
                <Droplet size={20} strokeWidth={2.5} className="text-red-400 mb-1" />
                <p className="text-xs text-gray-500">Grupo sanguíneo</p>
                <p className="text-2xl font-bold text-gray-900">{profile.blood_type}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Grid 3 tarjetas */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">

        {/* Información personal */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4 md:p-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-7 h-7 rounded-full bg-primary-light flex items-center justify-center flex-shrink-0">
              <User size={15} strokeWidth={2.5} className="text-primary-mid" />
            </div>
            <p className="text-sm font-medium text-gray-700">Información personal</p>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {profile?.birthdate && (
              <>
                <div>
                  <p className="text-xs text-gray-400 flex items-center gap-1"><Calendar size={11} strokeWidth={2.5} /> Fecha de nacimiento</p>
                  <p className="text-sm font-medium text-gray-900">{new Date(profile.birthdate + "T00:00:00").toLocaleDateString("es-CL")}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400 flex items-center gap-1"><User size={11} strokeWidth={2.5} /> Edad</p>
                  <p className="text-sm font-medium text-gray-900">{calcularEdad(profile.birthdate)} años</p>
                </div>
              </>
            )}
            {profile?.genre && (
              <div>
                <p className="text-xs text-gray-400 flex items-center gap-1"><User size={11} strokeWidth={2.5}/> Sexo</p>
                <p className="text-sm font-medium text-gray-900">{profile.genre}</p>
              </div>
            )}
            {profile?.weight && (
              <div>
                <p className="text-xs text-gray-400 flex items-center gap-1"><Weight size={11} strokeWidth={2.5} /> Peso</p>
                <p className="text-sm font-medium text-gray-900">{profile.weight} kg</p>
              </div>
            )}
            {profile?.height && (
              <div>
                <p className="text-xs text-gray-400 flex items-center gap-1"><Ruler size={11} strokeWidth={2.5} /> Altura</p>
                <p className="text-sm font-medium text-gray-900">{profile.height} cm</p>
              </div>
            )}
          </div>
        </div>

        {/* Contacto de emergencia */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4 md:p-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-7 h-7 rounded-full bg-primary-light flex items-center justify-center flex-shrink-0">
              <Phone size={15} strokeWidth={2.5} className="text-primary-mid" />
            </div>
            <p className="text-sm font-medium text-gray-700">Contacto de emergencia</p>
          </div>
          {profile?.emergency_contact_name ? (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-full bg-primary-light flex items-center justify-center text-primary-mid text-xs font-semibold flex-shrink-0">
                  {profile.emergency_contact_name[0]}
                </div>
                <p className="text-sm font-medium text-gray-900 truncate">{profile.emergency_contact_name}</p>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <div className="w-7 h-7 rounded-full bg-green-50 flex items-center justify-center flex-shrink-0">
                  <Phone size={13} strokeWidth={2.5} className="text-green-600" />
                </div>
                <span className="truncate">{profile.emergency_contact_phone || "—"}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <div className="w-7 h-7 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0">
                  <Mail size={13} strokeWidth={2.5} className="text-blue-600" />
                </div>
                <span className="text-gray-400">No registrado</span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-400">Sin contacto registrado</p>
          )}
        </div>

        {/* Medicamentos actuales */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4 md:p-6 sm:col-span-2 lg:col-span-1">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-7 h-7 rounded-full bg-primary-light flex items-center justify-center flex-shrink-0">
              <Activity size={15} strokeWidth={2.5} className="text-primary-mid" />
            </div>
            <p className="text-sm font-medium text-gray-700">Medicamentos actuales</p>
          </div>
          <p className="text-sm text-gray-400">Sin medicamentos registrados</p>
          <button className="flex items-center gap-1 text-xs text-primary-mid hover:underline mt-3">
            + Agregar medicamento
          </button>
        </div>

      </div>

      {/* Historial clínico reciente */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4 md:p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-primary-light flex items-center justify-center flex-shrink-0">
              <Clock size={15} strokeWidth={2.5} className="text-primary-mid" />
            </div>
            <p className="text-sm font-medium text-gray-700">Historial clínico reciente</p>
          </div>
          <button className="text-xs text-primary-mid hover:underline flex items-center gap-1">
            Ver todo →
          </button>
        </div>
        <p className="text-sm text-gray-400 text-center py-4">Sin historial registrado</p>
      </div>

    </div>
  );
}