import { useCallback } from 'react';

import Button from '@mui/material/Button';
import { Theme, SxProps } from '@mui/material/styles';

import { paths } from 'src/routes/paths';
import { useRouter } from 'src/routes/hooks';

import { useNavigate } from 'react-router-dom';


// ----------------------------------------------------------------------

type Props = {
  sx?: SxProps<Theme>;
  returnTo: string;
};
export default function LoginButton({ sx, returnTo }: Props) {
  const router = useRouter();

  const navigate = useNavigate();

  const handleClick = useCallback(() => {
    navigate(paths.auth.jwt.loginRedirect(returnTo));
  }, [returnTo, router])
  
  return (
    <Button onClick={handleClick} variant="outlined" sx={{ mr: 1, ...sx }}>
      Login
    </Button>
  );
}
