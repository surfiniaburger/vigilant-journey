'use client';

import { useAuth } from '@/context/AuthContext';
import { auth } from '@/lib/firebase';
import { GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { useRouter } from 'next/navigation';
import React from 'react';

interface ProtectedLinkProps {
  href: string;
  children: React.ReactNode;
}

// Type guard to check if the error is a Firebase Auth error
function isFirebaseAuthError(error: unknown): error is { code: string } {
    return (
        typeof error === 'object' &&
        error !== null &&
        'code' in error
    );
}


export const ProtectedLink = ({ href, children }: ProtectedLinkProps) => {
  const { user, loading } = useAuth();
  const router = useRouter();

  const handleSignInAndRedirect = async () => {
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
      router.push(href);
    } catch (error) {
      if (isFirebaseAuthError(error) && error.code === 'auth/popup-closed-by-user') {
        // User closed the popup. This is not an error we need to log.
        return;
      }
      console.error("Error signing in with Google", error);
    }
  };

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (loading) {
      return; // Do nothing while auth state is loading
    }
    if (user) {
      router.push(href);
    } else {
      handleSignInAndRedirect();
    }
  };

  return (
    <a href={href} onClick={handleClick}>
      {children}
    </a>
  );
};
