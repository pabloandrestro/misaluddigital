import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api } from "@/lib/api/client";
import { useAuthStore } from "@/lib/store/auth.store";
import loginIllustration from "@/assets/img/login-illustration.png";
import logoSaludaldia from "@/assets/logo/logo-saludaldia.png";
import textoSaludaldia from "@/assets/logo/texto.png";

const schema = z.object({
  email: z.string().email("Correo inválido"),
  password: z.string().min(1, "Ingresa tu contraseña"),
});

type FormData = z.infer<typeof schema>;

export default function LoginPage() {
  const navigate = useNavigate();
  const setUser = useAuthStore((s) => s.setUser);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    try {
      // Paso 1: verificar credenciales
      await api.post("/auth/login/", data);
      // Paso 2: obtener datos del usuario desde /auth/me/
      // El login no devuelve el objeto user por seguridad,
      // por eso hacemos una segunda llamada con el email      
      const meRes = await api.get(`/auth/me/?email=${data.email}`);
      setUser(meRes.data.user);

      toast.success(`Bienvenido, ${meRes.data.user.name}`);
      navigate("/");
    } catch {
      toast.error("Correo o contraseña incorrectos");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white px-4 py-0">
      <section className="w-full max-w-5xl rounded-[32px] border border-[var(--brand-subtle)] bg-[#f7f7f7] p-4 md:p-6 lg:p-8">
        <div className="grid items-center gap-10 lg:grid-cols-2">
          <div className="hidden h-full flex-col justify-between lg:flex">
            <div>
              <div className="mb-10 flex items-center gap-3">
                <img
                  src={logoSaludaldia}
                  alt="Logo Saludaldia"
                  className="h-12 w-auto object-contain"
                />

                <img
                  src={textoSaludaldia}
                  alt="Saludaldia"
                  className="h-8 w-auto object-contain"
                />
              </div>

              <h2 className="max-w-sm text-4xl font-bold leading-tight text-gray-800">
                Tu historial médico siempre contigo
              </h2>

              <p className="mt-3 max-w-xs text-base font-semibold leading-snug text-gray-500">
                Guarda, organiza y comparte tus documentos médicos de forma segura.
              </p>
            </div>

            <div className="my-4 flex justify-center">
              <img
                src={loginIllustration}
                alt="Historial médico digital"
                className="w-full max-w-sm object-contain"
              />
            </div>

            <div className="flex items-center gap-3 text-sm font-semibold text-gray-600">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[var(--brand-dark)] text-white">
                ✓
              </div>
              <span>Seguro</span>
              <span>•</span>
              <span>Privado</span>
              <span>•</span>
              <span>Confiable</span>
            </div>
          </div>

          <div className="mx-auto w-full max-w-md rounded-[36px] bg-white px-6 py-10 shadow-sm md:px-12 md:py-12">
            <div className="mb-8 text-center">
              <h1 className="text-3xl font-bold text-gray-950">
                Iniciar sesión
              </h1>
              <p className="mt-4 text-sm text-gray-500">
                Ingresa para acceder a tu cuenta
              </p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-900">
                  Correo electrónico
                </label>
                <input
                  {...register("email")}
                  type="email"
                  placeholder="tu@correo.cl"
                  className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm text-gray-800 outline-none transition focus:border-[var(--brand-mid)] focus:ring-2 focus:ring-[var(--brand-subtle)]"
                />
                {errors.email && (
                  <p className="mt-1 text-xs text-red-500">
                    {errors.email.message}
                  </p>
                )}
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-gray-900">
                  Contraseña
                </label>
                <input
                  {...register("password")}
                  type="password"
                  placeholder="Ingresa tu contraseña"
                  className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm text-gray-800 outline-none transition focus:border-[var(--brand-mid)] focus:ring-2 focus:ring-[var(--brand-subtle)]"
                />
                {errors.password && (
                  <p className="mt-1 text-xs text-red-500">
                    {errors.password.message}
                  </p>
                )}
              </div>

              <div className="flex items-center justify-between gap-4 text-sm">
                <label className="flex items-center gap-2 font-semibold text-gray-800">
                  <input
                    type="checkbox"
                    className="h-5 w-5 rounded border-gray-300 text-[var(--brand-dark)] focus:ring-[var(--brand-mid)]"
                  />
                  Recordarme
                </label>

                <Link
                  to="/forgot-password"
                  className="font-medium text-[var(--brand-dark)] hover:underline"
                >
                  ¿Olvidaste tu contraseña?
                </Link>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full rounded-lg bg-[var(--brand-dark)] py-3 text-lg font-medium text-white transition hover:bg-brand-600 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isSubmitting ? "Ingresando..." : "Iniciar sesión"}
              </button>
            </form>

            <p className="mt-10 text-center text-sm text-gray-900">
              ¿No tienes cuenta?{" "}
              <Link
                to="/signup"
                className="ml-4 font-medium text-[var(--brand-dark)] hover:underline"
              >
                Crear cuenta
              </Link>
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}