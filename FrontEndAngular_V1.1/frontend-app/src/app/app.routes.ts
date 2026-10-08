import type { Routes } from '@angular/router';
import { AppLayoutComponent } from '../widgets/layout/app-layout.component';
import { LoginPageComponent } from '../pages/login/login-page.component';
import { VerificarCorreoPageComponent } from '../pages/verificar-correo/verificar-correo-page.component';
import { CambioContrasenaVencidaPageComponent } from '../pages/cambio-vencido/cambio-contrasena-vencida-page.component';
import { CambioContrasenaTemporalPageComponent } from '../pages/cambio-temporal/cambio-contrasena-temporal-page.component';
import { LoginOtpPageComponent } from '../pages/login-otp/login-otp-page.component';
import { NotFoundPageComponent } from '../pages/not-found/not-found-page.component';
import { protectedGuard, publicGuard, requireModulo } from './router/guards';

export const routes: Routes = [
  { path: 'verificar-correo', component: VerificarCorreoPageComponent },
  { path: 'cambiar-contrasena-vencida', component: CambioContrasenaVencidaPageComponent },
  { path: 'cambiar-contrasena-temporal', component: CambioContrasenaTemporalPageComponent },
  { path: 'login/otp', component: LoginOtpPageComponent },

  { path: 'login', component: LoginPageComponent, canActivate: [publicGuard] },

  {
    path: '',
    component: AppLayoutComponent,
    canActivate: [protectedGuard],
    canActivateChild: [protectedGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      {
        path: 'dashboard',
        loadComponent: () =>
          import('../pages/dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
      },

      // Rutas respaldadas por un module_code: gating por puede_ver
      {
        path: 'sapin',
        canActivate: [requireModulo('SAPIN')],
        loadComponent: () => import('../pages/sapin/sapin-page.component').then((m) => m.SapinPageComponent),
      },
      {
        path: 'reportes',
        canActivate: [requireModulo('REPORTES')],
        loadComponent: () =>
          import('../pages/reportes/reportes-page.component').then((m) => m.ReportesPageComponent),
      },
      {
        path: 'ejecutivos',
        canActivate: [requireModulo('EJECUTIVOS')],
        loadComponent: () =>
          import('../pages/ejecutivos/ejecutivos-page.component').then((m) => m.EjecutivosPageComponent),
      },
      {
        path: 'canales',
        canActivate: [requireModulo('CANALES')],
        loadComponent: () => import('../pages/canales/canales-page.component').then((m) => m.CanalesPageComponent),
      },
      {
        path: 'oficinas',
        canActivate: [requireModulo('OFICINAS')],
        loadComponent: () =>
          import('../pages/oficinas/oficinas-page.component').then((m) => m.OficinasPageComponent),
      },
      {
        path: 'asesor-consumo',
        canActivate: [requireModulo('ASESOR_CONSUMO')],
        loadComponent: () =>
          import('../pages/asesor-consumo/asesor-consumo-page.component').then(
            (m) => m.AsesorConsumoPageComponent,
          ),
      },
      {
        path: 'asesor-movilidad',
        canActivate: [requireModulo('ASESOR_MOVILIDAD')],
        loadComponent: () =>
          import('../pages/asesor-movilidad/asesor-movilidad-page.component').then(
            (m) => m.AsesorMovilidadPageComponent,
          ),
      },
      {
        path: 'perfil-consumo',
        canActivate: [requireModulo('PERFIL_COMISIONISTA_CONSUMO')],
        loadComponent: () =>
          import('../pages/perfil/perfil-consumo-page.component').then((m) => m.PerfilConsumoPageComponent),
      },
      {
        path: 'perfil-movilidad',
        canActivate: [requireModulo('PERFIL_COMISIONISTA_MOVILIDAD')],
        loadComponent: () =>
          import('../pages/perfil/perfil-movilidad-page.component').then(
            (m) => m.PerfilMovilidadPageComponent,
          ),
      },

      // Sin module_code: solo requieren sesion (comportamiento actual)
      {
        path: 'documentos',
        loadComponent: () =>
          import('../pages/documentos/documentos-page.component').then((m) => m.DocumentosPageComponent),
      },
      {
        path: 'referencias',
        loadComponent: () =>
          import('../pages/referencias/referencias-page.component').then((m) => m.ReferenciasPageComponent),
      },
      {
        path: 'configuraciones',
        loadComponent: () =>
          import('../pages/configuraciones/configuraciones-page.component').then(
            (m) => m.ConfiguracionesPageComponent,
          ),
      },
      {
        path: 'configuraciones/cambio_contrasena',
        loadComponent: () =>
          import('../pages/configuraciones/cambio-contrasena-page.component').then(
            (m) => m.CambioContrasenaPageComponent,
          ),
      },
      {
        path: 'configuraciones/sesiones',
        loadComponent: () =>
          import('../pages/configuraciones/sesiones-activas-page.component').then(
            (m) => m.SesionesActivasPageComponent,
          ),
      },

      // Panel de Control y subpaginas: gating por PANEL_ADMIN
      {
        path: 'admin',
        canActivate: [requireModulo('PANEL_ADMIN')],
        children: [
          {
            path: 'dashboard',
            loadComponent: () =>
              import('../pages/admin/panel-admin-page.component').then((m) => m.PanelAdminPageComponent),
          },
          {
            path: 'catalogos',
            loadComponent: () =>
              import('../pages/admin/catalogos-admin-page.component').then(
                (m) => m.CatalogosAdminPageComponent,
              ),
          },
          {
            path: 'usuarios',
            loadComponent: () =>
              import('../pages/admin/usuarios-admin-page.component').then(
                (m) => m.UsuariosAdminPageComponent,
              ),
          },
          {
            path: 'afp',
            loadComponent: () =>
              import('../pages/admin/afp-admin-page.component').then((m) => m.AfpAdminPageComponent),
          },
          {
            path: 'arl',
            loadComponent: () =>
              import('../pages/admin/arl-admin-page.component').then((m) => m.ArlAdminPageComponent),
          },
          {
            path: 'eps',
            loadComponent: () =>
              import('../pages/admin/eps-admin-page.component').then((m) => m.EpsAdminPageComponent),
          },
          {
            path: 'bancos',
            loadComponent: () =>
              import('../pages/admin/bancos-admin-page.component').then((m) => m.BancosAdminPageComponent),
          },
          {
            path: 'profesiones',
            loadComponent: () =>
              import('../pages/admin/profesiones-admin-page.component').then(
                (m) => m.ProfesionesAdminPageComponent,
              ),
          },
          {
            path: 'departamentos',
            loadComponent: () =>
              import('../pages/admin/departamentos-admin-page.component').then(
                (m) => m.DepartamentosAdminPageComponent,
              ),
          },
          {
            path: 'ciudades',
            loadComponent: () =>
              import('../pages/admin/ciudades-admin-page.component').then(
                (m) => m.CiudadesAdminPageComponent,
              ),
          },
          {
            path: 'programas',
            loadComponent: () =>
              import('../pages/admin/programas-admin-page.component').then(
                (m) => m.ProgramasAdminPageComponent,
              ),
          },
          {
            path: 'subprogramas',
            loadComponent: () =>
              import('../pages/admin/subprogramas-admin-page.component').then(
                (m) => m.SubprogramasAdminPageComponent,
              ),
          },
          {
            path: 'autorizaciones',
            loadComponent: () =>
              import('../pages/admin/autorizaciones-admin-page.component').then(
                (m) => m.AutorizacionesAdminPageComponent,
              ),
          },
        ],
      },

      { path: '**', component: NotFoundPageComponent },
    ],
  },
];
