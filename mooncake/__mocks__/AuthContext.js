
import React from 'react';
import { AuthContext } from '@/context/AuthContext';

export const MockAuthProvider = ({ children }) => {
  const user = { uid: 'test-uid', email: 'test@example.com' };
  const loading = false;
  return (
    <AuthContext.Provider value={{ user, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
