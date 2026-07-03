import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api } from "@/lib/api/client";
import loginIllustration from "@/assets/img/login-illustration.png";
import logoSaludaldia from "@/assets/logo/logo-saludaldia.png";
import textoSaludaldia from "@/assets/logo/texto.png";

const schema = z
  .object({
    name: z.string().min(1, "Ingresa tu nombre completo"),
    email: z.string().email("Correo inválido"),
    rut: z.string().min(1, "Ingresa tu RUT"),
    password: z
      .string()
      .min(6, "Mínimo 6 caracteres")
      .max(12, "Máximo 12 caracteres")
      .regex(/[A-Z]/, "Debe tener al menos una mayúscula")
      .regex(/[a-z]/, "Debe tener al menos una minúscula")
      .regex(/[0-9]/, "Debe tener al menos un número")
      .regex(/[^A-Za-z0-9]/, "Debe tener al menos un símbolo"),
    confirmPassword: z.string(),
    terms: z.boolean().refine((value) => value === true, {
      message: "Debes aceptar los términos y condiciones",
    }),
  })
  .refine((d) => d.password === d.confirmPassword, {
    message: "Las contraseñas no coinciden",
    path: ["confirmPassword"],
  });

type FormData = z.infer<typeof schema>;

export default function SignupPage() {
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      terms: false,
    },
  });

  const onSubmit = async (data: FormData) => {
    try {
      const { confirmPassword, terms, ...payload } = data;

      await api.post("/auth/register/", payload);

      toast.success("Cuenta creada correctamente.");
      navigate("/complete-profile");
    } catch (err: any) {
      const errors = err?.response?.data?.errors;
      const firstError = errors && Object.values(errors).flat()[0];
      toast.error(
        typeof firstError === "string"
          ? firstError
          : err?.response?.data?.message ?? "Error al crear la cuenta"
      );
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-white px-4">
      <section className="w-full max-w-5xl rounded-[32px] border border-[var(--brand-subtle)] bg-[#f7f7f7] p-4 md:p-6 lg:p-8">
        <div className="grid items-center gap-8 lg:grid-cols-2">
          <div className="hidden h-full flex-col justify-between lg:flex">
            <div>
              <div className="mb-8 flex items-center gap-3">
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

          <div className="relative mx-auto w-full max-w-[440px] rounded-[36px] bg-white px-6 py-8 shadow-sm md:px-10 md:py-9">
            <Link
              to="/login"
              className="absolute left-6 top-7 text-3xl leading-none text-gray-500 transition hover:text-[var(--brand-dark)]"
              aria-label="Volver al login"
            >
              ‹
            </Link>

            <div className="mb-6 text-center">
              <h1 className="text-3xl font-bold text-gray-950">
                Crear cuenta
              </h1>
              <p className="mt-2 text-sm text-gray-500">
                Completa tus datos para comenzar
              </p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-2.5">
              {[
                {
                  name: "name",
                  label: "Nombre completo",
                  type: "text",
                  placeholder: "Ej. Juan Pérez",
                  error: errors.name?.message,
                },
                {
                  name: "rut",
                  label: "Rut",
                  type: "text",
                  placeholder: "Ej: 12.345.678-9",
                  error: errors.rut?.message,
                },
                {
                  name: "email",
                  label: "Correo electrónico",
                  type: "email",
                  placeholder: "tu@correo.cl",
                  error: errors.email?.message,
                },
                {
                  name: "password",
                  label: "Contraseña",
                  type: "password",
                  placeholder: "Crea una contraseña segura",
                  error: errors.password?.message,
                },
                {
                  name: "confirmPassword",
                  label: "Confirma contraseña",
                  type: "password",
                  placeholder: "Repite tu contraseña",
                  error: errors.confirmPassword?.message,
                },
              ].map((field) => (
                <div key={field.name}>
                  <label className="mb-1 block text-sm font-medium text-gray-900">
                    {field.label}
                  </label>
                  <input
                    {...register(field.name as keyof FormData)}
                    type={field.type}
                    placeholder={field.placeholder}
                    className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm text-gray-800 outline-none transition focus:border-[var(--brand-mid)] focus:ring-2 focus:ring-[var(--brand-subtle)]"
                  />
                  {field.error && (
                    <p className="mt-1 text-xs text-red-500">{field.error}</p>
                  )}
                </div>
              ))}

              <div className="pt-4">
                <label className="flex items-start gap-3 text-sm font-medium text-gray-800">
                  <input
                    {...register("terms")}
                    type="checkbox"
                    className="mt-1 h-5 w-5 rounded border-gray-300 text-[var(--brand-dark)] focus:ring-[var(--brand-mid)]"
                  />
                  <span className="leading-5">
                    Acepto los{" "}
                    <a
                      href="#"
                      className="text-[var(--brand-dark)] hover:underline"
                    >
                      Términos y condiciones
                    </a>{" "}
                    y la{" "}
                    <a
                      href="#"
                      className="text-[var(--brand-dark)] hover:underline"
                    >
                      Política de Privacidad
                    </a>
                  </span>
                </label>

                {errors.terms && (
                  <p className="mt-1 text-xs text-red-500">
                    {errors.terms.message}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="mt-3 w-full rounded-lg bg-[var(--brand-dark)] py-3 text-base font-medium text-white transition hover:bg-[var(--brand-mid)] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isSubmitting ? "Creando..." : "Crear cuenta"}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-gray-900">
              ¿Ya tienes cuenta?{" "}
              <Link
                to="/login"
                className="ml-3 font-medium text-[var(--brand-dark)] hover:underline"
              >
                Iniciar sesión
              </Link>
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
