import { lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '../../widgets/layout/AppLayout';
import { LoginPage } from '../../pages/login/LoginPage';
import { VerificarCorreoPage } from '../../pages/verificar-correo/VerificarCorreoPage';
import { CambioContrasenaVencidaPage } from '../../pages/cambio-vencido/CambioContrasenaVencidaPage';
import { CambioContrasenaTemporalPage } from '../../pages/cambio-temporal/CambioContrasenaTemporalPage';
import { LoginOtpPage } from '../../pages/login-otp/LoginOtpPage';
import { NotFoundPage } from '../../pages/not-found/NotFoundPage';
import { ProtectedRoute } from './ProtectedRoute';
import { PublicRoute } from './PublicRoute';
import { RequireModulo } from './RequireModulo';

const DashboardPage    = lazy(() => import('../../pages/dashboard/DashboardPage').then((module) => ({ default: module.DashboardPage })));
const SapinPage        = lazy(() => import('../../pages/sapin/SapinPage').then((module) => ({ default: module.SapinPage })));
const ReportesPage     = lazy(() => import('../../pages/reportes/ReportesPage').then((module) => ({ default: module.ReportesPage })));
const DocumentosPage   = lazy(() => import('../../pages/documentos/DocumentosPage').then((module) => ({ default: module.DocumentosPage })));
const ReferenciasPage  = lazy(() => import('../../pages/referencias/ReferenciasPage').then((module) => ({ default: module.ReferenciasPage })));
const EjecutivosPage        = lazy(() => import('../../pages/ejecutivos/EjecutivosPage').then((module) => ({ default: module.EjecutivosPage })));
const CanalesPage           = lazy(() => import('../../pages/canales/CanalesPage').then((module) => ({ default: module.CanalesPage })));
const OficinasPage          = lazy(() => import('../../pages/oficinas/OficinasPage').then((module) => ({ default: module.OficinasPage })));
const ConfiguracionesPage   = lazy(() => import('../../pages/configuraciones/ConfiguracionesPage').then((module) => ({ default: module.ConfiguracionesPage })));
const CambioContrasenaPage  = lazy(() => import('../../pages/configuraciones/CambioContrasenaPage').then((module) => ({ default: module.CambioContrasenaPage })));
const SesionesActivasPage   = lazy(() => import('../../pages/configuraciones/SesionesActivasPage').then((module) => ({ default: module.SesionesActivasPage })));
const AsesorConsumoPage     = lazy(() => import('../../pages/asesor-consumo/AsesorConsumoPage').then((module) => ({ default: module.AsesorConsumoPage })));
const AsesorMovilidadPage   = lazy(() => import('../../pages/asesor-movilidad/AsesorMovilidadPage').then((module) => ({ default: module.AsesorMovilidadPage })));
const PerfilConsumoPage     = lazy(() => import('../../pages/perfil/PerfilConsumoPage').then((module) => ({ default: module.PerfilConsumoPage })));
const PerfilMovilidadPage   = lazy(() => import('../../pages/perfil/PerfilMovilidadPage').then((module) => ({ default: module.PerfilMovilidadPage })));
const PanelAdminPage          = lazy(() => import('../../pages/admin/PanelAdminPage').then((module) => ({ default: module.PanelAdminPage })));
const CatalogosAdminPage      = lazy(() => import('../../pages/admin/CatalogosAdminPage').then((module) => ({ default: module.CatalogosAdminPage })));
const UsuariosAdminPage       = lazy(() => import('../../pages/admin/UsuariosAdminPage').then((module) => ({ default: module.UsuariosAdminPage })));
const AfpAdminPage            = lazy(() => import('../../pages/admin/AfpAdminPage').then((module) => ({ default: module.AfpAdminPage })));
const ArlAdminPage            = lazy(() => import('../../pages/admin/ArlAdminPage').then((module) => ({ default: module.ArlAdminPage })));
const EpsAdminPage            = lazy(() => import('../../pages/admin/EpsAdminPage').then((module) => ({ default: module.EpsAdminPage })));
const BancosAdminPage         = lazy(() => import('../../pages/admin/BancosAdminPage').then((module) => ({ default: module.BancosAdminPage })));
const ProfesionesAdminPage    = lazy(() => import('../../pages/admin/ProfesionesAdminPage').then((module) => ({ default: module.ProfesionesAdminPage })));
const DepartamentosAdminPage  = lazy(() => import('../../pages/admin/DepartamentosAdminPage').then((module) => ({ default: module.DepartamentosAdminPage })));
const CiudadesAdminPage       = lazy(() => import('../../pages/admin/CiudadesAdminPage').then((module) => ({ default: module.CiudadesAdminPage })));
const ProgramasAdminPage      = lazy(() => import('../../pages/admin/ProgramasAdminPage').then((module) => ({ default: module.ProgramasAdminPage })));
const SubprogramasAdminPage   = lazy(() => import('../../pages/admin/SubprogramasAdminPage').then((module) => ({ default: module.SubprogramasAdminPage })));
const AutorizacionesAdminPage = lazy(() => import('../../pages/admin/AutorizacionesAdminPage').then((module) => ({ default: module.AutorizacionesAdminPage })));

export function AppRouter() {
  return (
    <Routes>
      <Route path="/verificar-correo" element={<VerificarCorreoPage />} />
      <Route path="/cambiar-contrasena-vencida" element={<CambioContrasenaVencidaPage />} />
      <Route path="/cambiar-contrasena-temporal" element={<CambioContrasenaTemporalPage />} />
      <Route path="/login/otp" element={<LoginOtpPage />} />

      <Route element={<PublicRoute />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />

          {/* Rutas respaldadas por un module_code: gating por puede_ver */}
          <Route element={<RequireModulo modulo="SAPIN" />}>
            <Route path="/sapin" element={<SapinPage />} />
          </Route>
          <Route element={<RequireModulo modulo="REPORTES" />}>
            <Route path="/reportes" element={<ReportesPage />} />
          </Route>
          <Route element={<RequireModulo modulo="EJECUTIVOS" />}>
            <Route path="/ejecutivos" element={<EjecutivosPage />} />
          </Route>
          <Route element={<RequireModulo modulo="CANALES" />}>
            <Route path="/canales" element={<CanalesPage />} />
          </Route>
          <Route element={<RequireModulo modulo="OFICINAS" />}>
            <Route path="/oficinas" element={<OficinasPage />} />
          </Route>
          <Route element={<RequireModulo modulo="ASESOR_CONSUMO" />}>
            <Route path="/asesor-consumo" element={<AsesorConsumoPage />} />
          </Route>
          <Route element={<RequireModulo modulo="ASESOR_MOVILIDAD" />}>
            <Route path="/asesor-movilidad" element={<AsesorMovilidadPage />} />
          </Route>
          <Route element={<RequireModulo modulo="PERFIL_COMISIONISTA_CONSUMO" />}>
            <Route path="/perfil-consumo" element={<PerfilConsumoPage />} />
          </Route>
          <Route element={<RequireModulo modulo="PERFIL_COMISIONISTA_MOVILIDAD" />}>
            <Route path="/perfil-movilidad" element={<PerfilMovilidadPage />} />
          </Route>

          {/* Sin module_code: solo requieren sesion (comportamiento actual) */}
          <Route path="/documentos" element={<DocumentosPage />} />
          <Route path="/referencias" element={<ReferenciasPage />} />
          <Route path="/configuraciones" element={<ConfiguracionesPage />} />
          <Route path="/configuraciones/cambio_contrasena" element={<CambioContrasenaPage />} />
          <Route path="/configuraciones/sesiones" element={<SesionesActivasPage />} />

          {/* Panel de Control y subpaginas: gating por PANEL_ADMIN */}
          <Route element={<RequireModulo modulo="PANEL_ADMIN" />}>
            <Route path="/admin/dashboard" element={<PanelAdminPage />} />
            <Route path="/admin/catalogos" element={<CatalogosAdminPage />} />
            <Route path="/admin/usuarios" element={<UsuariosAdminPage />} />
            <Route path="/admin/afp" element={<AfpAdminPage />} />
            <Route path="/admin/arl" element={<ArlAdminPage />} />
            <Route path="/admin/eps" element={<EpsAdminPage />} />
            <Route path="/admin/bancos" element={<BancosAdminPage />} />
            <Route path="/admin/profesiones" element={<ProfesionesAdminPage />} />
            <Route path="/admin/departamentos" element={<DepartamentosAdminPage />} />
            <Route path="/admin/ciudades" element={<CiudadesAdminPage />} />
            <Route path="/admin/programas" element={<ProgramasAdminPage />} />
            <Route path="/admin/subprogramas" element={<SubprogramasAdminPage />} />
            <Route path="/admin/autorizaciones" element={<AutorizacionesAdminPage />} />
          </Route>

          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Route>
    </Routes>
  );
}