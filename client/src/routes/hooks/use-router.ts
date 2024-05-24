import { useNavigate, useLocation } from 'react-router-dom';

// Exporting hooks similar to useRouter
export const useRouter = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  return { navigate, location };
};
