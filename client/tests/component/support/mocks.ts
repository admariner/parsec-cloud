// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

import { NotificationKey } from '@/services/notificationManager';
import { translate } from '@/services/translation';
import { config } from '@vue/test-utils';
import { vi } from 'vitest';

async function mockShowToast(_notif: Notification): Promise<void> {
  // Do nothing
}

function getDefaultProvideConfig(showToast = mockShowToast): any {
  const provide: any = {};

  provide[NotificationKey] = {
    showToast: showToast,
  };

  return provide;
}

function mockValidators(): void {
  vi.mock('@/parsec', async () => {
    const parsec = await vi.importActual<typeof import('@/parsec')>('@/parsec');
    return {
      ...parsec,
      isValidOrganizationName: async (_value: string): Promise<boolean> => {
        return false;
      },
      parseBackendAddr: async (_value: string): Promise<any> => {
        return { ok: false, error: 'error' };
      },
    };
  });
}

function mockI18n(): void {
  config.global.mocks = {
    $t: (key: string, attrs?: object, count?: number): string => translate(key, attrs, count),
  };
}

interface Route {
  route: string;
  params?: object;
  query?: object;
}

const ROUTES_CALLED: Array<Route> = [];

function mockRouter(): void {
  // Mocking the following import:
  // import { useRouter } from 'vue-router';
  vi.mock('vue-router', async () => {
    const router = await vi.importActual<typeof import('vue-router')>('vue-router');
    return {
      ...router,
      useRouter: (): any => {
        return {
          push: (options: any): void => {
            ROUTES_CALLED.push({ route: options.name, params: options.params, query: options.query });
          },
        };
      },
    };
  });
}

function getRoutesCalled(): Array<Route> {
  return ROUTES_CALLED;
}

function resetRoutesCalled(): void {
  ROUTES_CALLED.splice(0);
}

export { getDefaultProvideConfig, getRoutesCalled, mockI18n, mockRouter, mockValidators, resetRoutesCalled };
