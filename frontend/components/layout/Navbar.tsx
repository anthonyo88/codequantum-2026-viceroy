"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { LogOut, ChevronDown, Users, Bookmark, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { useAuth } from "@/lib/context/AuthContext";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";

const NAV_LINKS = [
  { href: "/drivers", label: "Drivers", icon: Users },
  { href: "/shortlists", label: "Shortlists", icon: Bookmark },
  { href: "/chat", label: "AI Search", icon: MessageSquare },
];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-16 bg-surface/80 backdrop-blur-sm border-b border-border flex items-center px-6">
      {/* Logo */}
      <Link href="/drivers" className="flex items-center gap-2 mr-8">
        <div className="w-7 h-7 bg-accent rounded flex items-center justify-center flex-shrink-0">
          <span className="text-white font-black text-xs">F1</span>
        </div>
        <span className="text-base font-bold text-text-primary tracking-tight hidden sm:block">
          F1 Recruit
        </span>
      </Link>

      {/* Nav links */}
      <nav className="flex items-center gap-1 flex-1">
        {NAV_LINKS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded text-sm font-medium transition-colors duration-150",
                active
                  ? "text-white bg-surface-elevated"
                  : "text-text-secondary hover:text-text-primary hover:bg-surface-hover"
              )}
            >
              <Icon className="w-4 h-4" />
              <span className="hidden md:block">{label}</span>
            </Link>
          );
        })}
      </nav>

      {/* User menu */}
      {user && (
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <button className="flex items-center gap-2 px-3 py-1.5 rounded hover:bg-surface-hover transition-colors duration-150 outline-none">
              <div className="w-7 h-7 rounded-full bg-accent-muted border border-accent/30 flex items-center justify-center">
                <span className="text-accent text-xs font-bold uppercase">
                  {user.email[0]}
                </span>
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-xs font-medium text-text-primary leading-none">
                  {user.company_name || user.email}
                </p>
                <p className="text-xs text-text-muted capitalize mt-0.5">
                  {user.role}
                </p>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-text-muted" />
            </button>
          </DropdownMenu.Trigger>

          <DropdownMenu.Portal>
            <DropdownMenu.Content
              align="end"
              sideOffset={4}
              className="bg-surface border border-border rounded-lg shadow-card-hover p-1 min-w-[160px] animate-slide-up z-50"
            >
              <DropdownMenu.Item
                onSelect={handleLogout}
                className="flex items-center gap-2 px-3 py-2 text-sm text-text-secondary hover:text-text-primary hover:bg-surface-hover rounded cursor-pointer outline-none transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Sign out
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
      )}
    </header>
  );
}
