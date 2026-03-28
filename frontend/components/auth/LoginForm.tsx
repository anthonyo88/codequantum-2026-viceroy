"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import toast from "react-hot-toast";
import { loginSchema, type LoginFormData } from "@/lib/schemas/auth";
import { useAuth } from "@/lib/context/AuthContext";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  async function onSubmit(data: LoginFormData) {
    try {
      await login(data);
      const from = searchParams.get("from") ?? "/drivers";
      router.push(from);
    } catch {
      setError("root", { message: "Invalid email or password" });
      toast.error("Login failed");
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
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
            Welcome back
          </h1>
          <p className="text-text-secondary text-sm mb-6">
            Sign in to your recruiting account
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
            <Input
              id="email"
              label="Email"
              type="email"
              placeholder="you@company.com"
              error={errors.email?.message}
              {...register("email")}
            />
            <Input
              id="password"
              label="Password"
              type="password"
              placeholder="••••••••"
              error={errors.password?.message}
              {...register("password")}
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
              Sign in
            </Button>
          </form>

          <p className="text-center text-sm text-text-muted mt-6">
            Don&apos;t have an account?{" "}
            <Link
              href="/register"
              className="text-accent hover:text-accent-hover font-medium transition-colors"
            >
              Register your company
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
