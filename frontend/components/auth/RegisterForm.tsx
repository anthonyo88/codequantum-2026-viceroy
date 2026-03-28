"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import Link from "next/link";
import toast from "react-hot-toast";
import { registerSchema, type RegisterFormData } from "@/lib/schemas/auth";
import { useAuth } from "@/lib/context/AuthContext";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

const COMPANY_TYPE_LABELS: Record<string, string> = {
  f1_team: "Formula 1 Team",
  formula2: "Formula 2 Team",
  formula3: "Formula 3 Team",
  indycar: "IndyCar",
  sponsor: "Sponsor / Partner",
  other: "Other",
};

export function RegisterForm() {
  const router = useRouter();
  const { register: authRegister } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: { company_type: "f1_team" },
  });

  async function onSubmit(data: RegisterFormData) {
    try {
      await authRegister({
        company_name: data.company_name,
        company_type: data.company_type,
        contact_email: data.contact_email,
        password: data.password,
      });
      toast.success("Account created successfully!");
      router.push("/drivers");
    } catch (err: any) {
      const msg =
        err?.response?.data?.detail ?? "Registration failed. Please try again.";
      setError("root", { message: msg });
      toast.error("Registration failed");
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="flex items-center gap-2 mb-8 justify-center">
          <div className="w-8 h-8 bg-accent rounded flex items-center justify-center">
            <span className="text-white font-black text-sm">F1</span>
          </div>
          <span className="text-xl font-bold text-text-primary tracking-tight">
            F1 R&B
          </span>
        </div>

        <div className="bg-surface border border-border rounded-xl p-8 shadow-card">
          <h1 className="text-2xl font-bold text-text-primary mb-1">
            Create account
          </h1>
          <p className="text-text-secondary text-sm mb-6">
            Register your company to start recruiting
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
            <Input
              id="company_name"
              label="Company name"
              placeholder="Red Bull Racing"
              error={errors.company_name?.message}
              {...register("company_name")}
            />

            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="company_type"
                className="text-sm font-medium text-text-secondary"
              >
                Company type
              </label>
              <select
                id="company_type"
                className="bg-surface border border-border rounded px-3 py-2 text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                {...register("company_type")}
              >
                {Object.entries(COMPANY_TYPE_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
              {errors.company_type && (
                <p className="text-xs text-red-400">
                  {errors.company_type.message}
                </p>
              )}
            </div>

            <Input
              id="contact_email"
              label="Contact email"
              type="email"
              placeholder="admin@team.com"
              error={errors.contact_email?.message}
              {...register("contact_email")}
            />

            <Input
              id="password"
              label="Password"
              type="password"
              placeholder="Min 8 characters"
              error={errors.password?.message}
              {...register("password")}
            />

            <Input
              id="confirm_password"
              label="Confirm password"
              type="password"
              placeholder="••••••••"
              error={errors.confirm_password?.message}
              {...register("confirm_password")}
            />

            {errors.root && (
              <p className="text-sm text-red-400 text-center">
                {errors.root.message}
              </p>
            )}

            <Button
              type="submit"
              size="lg"
              loading={isSubmitting}
              className="w-full mt-2"
            >
              Create account
            </Button>
          </form>

          <p className="text-center text-sm text-text-muted mt-6">
            Already have an account?{" "}
            <Link
              href="/login"
              className="text-accent hover:text-accent-hover font-medium transition-colors"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
