import Box from '@mui/material/Box';

import { useBoolean } from 'src/hooks/use-boolean';
import { useResponsive } from 'src/hooks/use-responsive';

import { useSettingsContext } from 'src/components/settings';

import Main from './main';
import Header from './header';
import NavVertical from './nav-vertical';

type Props = {
  children: React.ReactNode;
};

export default function MainLayout({ children }: Props) {
  const settings = useSettingsContext();

  const lgUp = useResponsive("up", "lg");

  const nav = useBoolean();

  return (
    <>
      <Header />
      <Box
        sx={{
          minHeight: 1,
          display: 'flex',
          flexDirection: { xs: 'column', lg: 'row' },
        }}
      >
        <NavVertical openNav={nav.value} onCloseNav={nav.onFalse} />
        <Main>{children}</Main>
      </Box>
    </>
  );
}
