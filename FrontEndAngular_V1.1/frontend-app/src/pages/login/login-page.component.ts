import { ChangeDetectionStrategy, Component } from '@angular/core';
import { LoginFormComponent } from '../../features/auth/ui/login-form.component';
import { BrandLogoComponent } from '../../shared/ui/components/brand-logo.component';
import { BrandShowcaseComponent } from './brand-showcase.component';

@Component({
  selector: 'app-login-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [LoginFormComponent, BrandLogoComponent, BrandShowcaseComponent],
  template: `
    <div class="login-page">
      <!-- Brand panel — landing animado -->
      <div class="login-page__brand">
        <app-brand-showcase />
      </div>

      <!-- Form panel -->
      <div class="login-page__form">
        <div style="width: 100%; max-width: 380px">
          <div class="mb-0">
            <app-brand-logo [height]="32" />
          </div>
          <app-login-form />
        </div>
      </div>
    </div>
  `,
})
export class LoginPageComponent {}
