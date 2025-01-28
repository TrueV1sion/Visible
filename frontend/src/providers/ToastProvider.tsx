import React from 'react';
import { ToastContainer, ToastContainerProps } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useTheme } from '@mui/material';

interface ToastProviderProps extends Partial<ToastContainerProps> {
  children: React.ReactNode;
}

const ToastProvider: React.FC<ToastProviderProps> = ({
  children,
  ...props
}) => {
  const theme = useTheme();

  return (
    <>
      {children}
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme={theme.palette.mode}
        style={{ fontSize: '0.875rem' }}
        toastStyle={{
          backgroundColor: theme.palette.background.paper,
          color: theme.palette.text.primary,
          borderRadius: theme.shape.borderRadius,
          boxShadow: theme.shadows[3],
        }}
        {...props}
      />
    </>
  );
};

export default ToastProvider; 