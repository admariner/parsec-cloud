// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

import { Locator, Page } from '@playwright/test';
import { expect } from '@tests/pw/helpers/assertions';
import { MockBms } from '@tests/pw/helpers/bms';
import { DEFAULT_ORGANIZATION_INFORMATION, DEFAULT_USER_INFORMATION } from '@tests/pw/helpers/data';
import { msTest } from '@tests/pw/helpers/fixtures';
import { fillInputModal, fillIonInput } from '@tests/pw/helpers/utils';

// cspell:disable-next-line
const _HOST = 'saas-demo-v3-mightyfairy.parsec.cloud';
// cspell:disable-next-line
const _PAYLOAD = 'xBCy2YVGB31DPzcxGZbGVUt7';
const BOOTSTRAP_ADDR = `parsec3://${_HOST}/BlackMesa?no_ssl=true&a=bootstrap_organization&p=${_PAYLOAD}`;

async function openCreateOrganizationModal(page: Page): Promise<Locator> {
  await page.locator('#create-organization-button').click();
  await page.locator('.popover-viewport').getByRole('listitem').nth(0).click();
  const modal = page.locator('.create-organization-modal');
  await modal.locator('.server-choice-item').nth(0).click();
  await modal.locator('.server-modal-footer').locator('ion-button').nth(1).click();
  return modal;
}

async function cancelAndResume(page: Page, currentContainer: Locator): Promise<void> {
  await expect(currentContainer.locator('.closeBtn')).toBeVisible();
  await currentContainer.locator('.closeBtn').click();
  await expect(page.locator('.create-organization-modal')).toBeHidden();
  await expect(page.locator('.question-modal')).toBeVisible();
  await page.locator('.question-modal').locator('#cancel-button').click();
  await expect(page.locator('.question-modal')).toBeHidden();
  await expect(page.locator('.create-organization-modal')).toBeVisible();
}

msTest('Go through saas org creation process', async ({ home }) => {
  const modal = await openCreateOrganizationModal(home);

  await MockBms.mockLogin(home);
  await MockBms.mockUserRoute(home);
  await MockBms.mockCreateOrganization(home, BOOTSTRAP_ADDR);

  const bmsContainer = modal.locator('.saas-login-container');
  await expect(bmsContainer.locator('.modal-header__title')).toHaveText('Link you customer account to your new organization');
  const bmsNext = bmsContainer.locator('.saas-login-footer').locator('ion-button').nth(0);
  await expect(bmsNext).toHaveDisabledAttribute();
  await fillIonInput(bmsContainer.locator('ion-input').nth(0), DEFAULT_USER_INFORMATION.email);
  await expect(bmsNext).toHaveDisabledAttribute();
  await fillIonInput(bmsContainer.locator('ion-input').nth(1), DEFAULT_USER_INFORMATION.password);
  await expect(bmsNext).not.toHaveDisabledAttribute();

  await cancelAndResume(home, bmsContainer);
  await bmsNext.click();

  const orgNameContainer = modal.locator('.organization-name-page');
  await expect(bmsContainer).toBeHidden();
  await expect(orgNameContainer).toBeVisible();
  await expect(orgNameContainer.locator('.modal-header__title')).toHaveText('Create an organization');
  const orgNameNext = modal.locator('.organization-name-page-footer').locator('ion-button');
  await expect(orgNameNext).toHaveDisabledAttribute();

  await cancelAndResume(home, orgNameContainer);

  // Invalid org name
  await fillIonInput(orgNameContainer.locator('ion-input').nth(0), 'Invalid Org N@me');
  await expect(orgNameNext).toHaveDisabledAttribute();
  const orgNameError = orgNameContainer.locator('#org-name-input').locator('.form-error');
  await expect(orgNameError).toBeVisible();
  await expect(orgNameError).toHaveText('Only letters, digits, underscores and hyphens. No spaces.');

  // Back to good name
  await fillIonInput(orgNameContainer.locator('ion-input'), DEFAULT_ORGANIZATION_INFORMATION.name);
  await expect(orgNameError).toBeHidden();
  await expect(orgNameNext).not.toHaveDisabledAttribute();

  await orgNameNext.click();

  const authContainer = modal.locator('.authentication-page');
  const authPrevious = modal.locator('.authentication-page-footer').locator('ion-button').nth(0);
  const authNext = modal.locator('.authentication-page-footer').locator('ion-button').nth(1);
  await expect(orgNameContainer).toBeHidden();
  await expect(bmsContainer).toBeHidden();
  await expect(authContainer).toBeVisible();
  await expect(authContainer.locator('.modal-header__title')).toHaveText('Authentication');
  await expect(authPrevious).toBeVisible();
  await expect(authPrevious).not.toHaveDisabledAttribute();
  await expect(authNext).toBeVisible();
  await expect(authNext).toHaveDisabledAttribute();
  await fillIonInput(authContainer.locator('.choose-password').locator('ion-input').nth(0), DEFAULT_USER_INFORMATION.password);
  await expect(authNext).toHaveDisabledAttribute();
  await fillIonInput(authContainer.locator('.choose-password').locator('ion-input').nth(1), DEFAULT_USER_INFORMATION.password);
  await expect(authNext).not.toHaveDisabledAttribute();

  // Try cancelling
  await cancelAndResume(home, authContainer);

  // Password too simple
  await fillIonInput(authContainer.locator('.choose-password').locator('ion-input').nth(0), 'EasyP@ssw0rd');
  await expect(authContainer.locator('.password-level__text')).toHaveText('Low');
  await expect(authNext).toHaveDisabledAttribute();

  // Back to complicated password
  await fillIonInput(authContainer.locator('.choose-password').locator('ion-input').nth(0), DEFAULT_USER_INFORMATION.password);
  await expect(authContainer.locator('.password-level__text')).toHaveText('Strong');
  await expect(authNext).not.toHaveDisabledAttribute();

  // Check does not match
  await fillIonInput(authContainer.locator('.choose-password').locator('ion-input').nth(1), `${DEFAULT_USER_INFORMATION.password}-extra`);
  await expect(authNext).toHaveDisabledAttribute();
  const matchError = authContainer.locator('.choose-password').locator('.inputs-container-item').nth(1).locator('.form-helperText').nth(1);
  await expect(matchError).toBeVisible();
  await expect(matchError).toHaveText('Do not match');

  // Back to matching password
  await fillIonInput(authContainer.locator('.choose-password').locator('ion-input').nth(1), DEFAULT_USER_INFORMATION.password);
  await expect(authNext).not.toHaveDisabledAttribute();
  await expect(matchError).toBeHidden();

  await authNext.click();

  const summaryContainer = modal.locator('.summary-page');
  const summaryPrevious = modal.locator('.summary-page-footer').locator('ion-button').nth(0);
  const summaryNext = modal.locator('.summary-page-footer').locator('ion-button').nth(1);
  await expect(orgNameContainer).toBeHidden();
  await expect(bmsContainer).toBeHidden();
  await expect(authContainer).toBeHidden();
  await expect(summaryContainer).toBeVisible();
  await expect(summaryContainer.locator('.modal-header__title')).toHaveText('Overview of your organization');
  await expect(summaryPrevious).toBeVisible();
  await expect(summaryPrevious).not.toHaveDisabledAttribute();
  await expect(summaryNext).toBeVisible();
  await expect(summaryNext).not.toHaveDisabledAttribute();

  await cancelAndResume(home, summaryContainer);

  await expect(summaryContainer.locator('.summary-item__label')).toHaveText([
    'Organization',
    'Full name',
    'Email',
    'Server choice',
    'Authentication method',
  ]);
  await expect(summaryContainer.locator('.summary-item__text')).toHaveText([
    DEFAULT_ORGANIZATION_INFORMATION.name,
    DEFAULT_USER_INFORMATION.name,
    DEFAULT_USER_INFORMATION.email,
    'Parsec SaaS',
    'Password',
  ]);
  await summaryNext.click();

  await expect(orgNameContainer).toBeHidden();
  await expect(bmsContainer).toBeHidden();
  await expect(authContainer).toBeHidden();
  await expect(summaryContainer).toBeHidden();
  await expect(modal.locator('.creation-page')).toBeVisible();
  await expect(modal.locator('.creation-page').locator('.closeBtn')).toBeHidden();
  await home.waitForTimeout(1000);

  await expect(modal.locator('.created-page')).toBeVisible();
  await expect(modal.locator('.creation-page')).toBeHidden();
  await expect(modal.locator('.created-page').locator('.closeBtn')).toBeHidden();
  await modal.locator('.created-page-footer').locator('ion-button').click();
  await expect(modal).toBeHidden();
});

msTest('Go through saas org creation process from bootstrap link', async ({ home }) => {
  await home.locator('#create-organization-button').click();
  await home.locator('.popover-viewport').getByRole('listitem').nth(1).click();
  await fillInputModal(home, BOOTSTRAP_ADDR);
  const modal = home.locator('.create-organization-modal');

  await MockBms.mockLogin(home);
  await MockBms.mockUserRoute(home);
  await MockBms.mockCreateOrganization(home, BOOTSTRAP_ADDR);

  const bmsContainer = modal.locator('.saas-login-container');
  await expect(bmsContainer.locator('.modal-header__title')).toHaveText('Link you customer account to your new organization');
  const bmsNext = bmsContainer.locator('.saas-login-footer').locator('ion-button').nth(0);
  await expect(bmsNext).toHaveDisabledAttribute();
  await fillIonInput(bmsContainer.locator('ion-input').nth(0), DEFAULT_USER_INFORMATION.email);
  await expect(bmsNext).toHaveDisabledAttribute();
  await fillIonInput(bmsContainer.locator('ion-input').nth(1), DEFAULT_USER_INFORMATION.password);
  await expect(bmsNext).not.toHaveDisabledAttribute();

  await bmsNext.click();

  const authContainer = modal.locator('.authentication-page');
  const authPrevious = modal.locator('.authentication-page-footer').locator('ion-button').nth(0);
  const authNext = modal.locator('.authentication-page-footer').locator('ion-button').nth(1);
  await expect(bmsContainer).toBeHidden();
  await expect(authContainer).toBeVisible();
  await expect(authContainer.locator('.modal-header__title')).toHaveText('Authentication');
  await expect(authPrevious).toBeVisible();
  await expect(authPrevious).not.toHaveDisabledAttribute();
  await expect(authNext).toBeVisible();
  await expect(authNext).toHaveDisabledAttribute();
  await fillIonInput(authContainer.locator('.choose-password').locator('ion-input').nth(0), DEFAULT_USER_INFORMATION.password);
  await expect(authNext).toHaveDisabledAttribute();
  await fillIonInput(authContainer.locator('.choose-password').locator('ion-input').nth(1), DEFAULT_USER_INFORMATION.password);
  await expect(authNext).not.toHaveDisabledAttribute();

  await authNext.click();

  const summaryContainer = modal.locator('.summary-page');
  const summaryPrevious = modal.locator('.summary-page-footer').locator('ion-button').nth(0);
  const summaryNext = modal.locator('.summary-page-footer').locator('ion-button').nth(1);
  await expect(bmsContainer).toBeHidden();
  await expect(authContainer).toBeHidden();
  await expect(summaryContainer).toBeVisible();
  await expect(summaryContainer.locator('.modal-header__title')).toHaveText('Overview of your organization');
  await expect(summaryPrevious).toBeVisible();
  await expect(summaryPrevious).not.toHaveDisabledAttribute();
  await expect(summaryNext).toBeVisible();
  await expect(summaryNext).not.toHaveDisabledAttribute();

  await cancelAndResume(home, summaryContainer);

  await expect(summaryContainer.locator('.summary-item__label')).toHaveText([
    'Organization',
    'Full name',
    'Email',
    'Server choice',
    'Authentication method',
  ]);
  await expect(summaryContainer.locator('.summary-item__text')).toHaveText([
    DEFAULT_ORGANIZATION_INFORMATION.name,
    DEFAULT_USER_INFORMATION.name,
    DEFAULT_USER_INFORMATION.email,
    'Parsec SaaS',
    'Password',
  ]);
  await summaryNext.click();

  await expect(bmsContainer).toBeHidden();
  await expect(authContainer).toBeHidden();
  await expect(summaryContainer).toBeHidden();
  await expect(modal.locator('.creation-page')).toBeVisible();
  await expect(modal.locator('.creation-page').locator('.closeBtn')).toBeHidden();
  await home.waitForTimeout(1000);

  await expect(modal.locator('.created-page')).toBeVisible();
  await expect(modal.locator('.creation-page')).toBeHidden();
  await expect(modal.locator('.created-page').locator('.closeBtn')).toBeHidden();
  await modal.locator('.created-page-footer').locator('ion-button').click();
  await expect(modal).toBeHidden();
});

msTest('Open account creation', async ({ home }) => {
  const modal = await openCreateOrganizationModal(home);

  const bmsContainer = modal.locator('.saas-login-container');
  await expect(bmsContainer.locator('.saas-login-footer').locator('ion-button').nth(1)).toHaveText('Create an account');
  const newTabPromise = home.waitForEvent('popup');
  await bmsContainer.locator('.saas-login-footer').locator('ion-button').nth(1).click();
  const newTab = await newTabPromise;
  await expect(newTab).toHaveURL(/^https:\/\/parsec\.cloud(?:\/en)\/tarification\/?$/);
});

msTest('Fail to login to BMS', async ({ home }) => {
  const modal = await openCreateOrganizationModal(home);

  await MockBms.mockLogin(home, { POST: { errors: { status: 401 } } });

  const bmsContainer = modal.locator('.saas-login-container');
  const bmsNext = bmsContainer.locator('.saas-login-footer').locator('ion-button').nth(0);
  await fillIonInput(bmsContainer.locator('ion-input').nth(0), DEFAULT_USER_INFORMATION.email);
  await fillIonInput(bmsContainer.locator('ion-input').nth(1), DEFAULT_USER_INFORMATION.password);
  await bmsNext.click();

  await expect(bmsContainer.locator('.login-button-error')).toBeVisible();
  await expect(bmsContainer.locator('.login-button-error')).toHaveText('Cannot log in. Please check your email and password.');
});

msTest('Cannot reach the BMS', async ({ home }) => {
  await MockBms.mockLogin(home, { POST: { timeout: true } });
  const modal = await openCreateOrganizationModal(home);

  const bmsContainer = modal.locator('.saas-login-container');
  const bmsNext = bmsContainer.locator('.saas-login-footer').locator('ion-button').nth(0);
  await fillIonInput(bmsContainer.locator('ion-input').nth(0), DEFAULT_USER_INFORMATION.email);
  await fillIonInput(bmsContainer.locator('ion-input').nth(1), DEFAULT_USER_INFORMATION.password);
  await bmsNext.click();

  await expect(bmsContainer.locator('.login-button-error')).toBeVisible();
  await expect(bmsContainer.locator('.login-button-error')).toHaveText(
    'Could not reach the server. Make sure that you are online and try again.',
  );
});

msTest('Edit from summary', async ({ home }) => {
  const modal = await openCreateOrganizationModal(home);

  await MockBms.mockLogin(home);
  await MockBms.mockUserRoute(home);
  await MockBms.mockCreateOrganization(home, BOOTSTRAP_ADDR);

  const bmsContainer = modal.locator('.saas-login-container');
  const bmsNext = bmsContainer.locator('.saas-login-footer').locator('ion-button').nth(0);
  await fillIonInput(bmsContainer.locator('ion-input').nth(0), DEFAULT_USER_INFORMATION.email);
  await fillIonInput(bmsContainer.locator('ion-input').nth(1), DEFAULT_USER_INFORMATION.password);
  await bmsNext.click();

  const orgNameContainer = modal.locator('.organization-name-page');
  const orgNameNext = modal.locator('.organization-name-page-footer').locator('ion-button');
  await fillIonInput(orgNameContainer.locator('ion-input'), DEFAULT_ORGANIZATION_INFORMATION.name);
  await orgNameNext.click();

  const authContainer = modal.locator('.authentication-page');
  const authNext = modal.locator('.authentication-page-footer').locator('ion-button').nth(1);
  await fillIonInput(authContainer.locator('.choose-password').locator('ion-input').nth(0), DEFAULT_USER_INFORMATION.password);
  await fillIonInput(authContainer.locator('.choose-password').locator('ion-input').nth(1), DEFAULT_USER_INFORMATION.password);
  await authNext.click();

  const summaryContainer = modal.locator('.summary-page');
  const summaryNext = modal.locator('.summary-page-footer').locator('ion-button').nth(1);

  await expect(summaryContainer.locator('.summary-item__label')).toHaveText([
    'Organization',
    'Full name',
    'Email',
    'Server choice',
    'Authentication method',
  ]);
  await expect(summaryContainer.locator('.summary-item__text')).toHaveText([
    DEFAULT_ORGANIZATION_INFORMATION.name,
    DEFAULT_USER_INFORMATION.name,
    DEFAULT_USER_INFORMATION.email,
    'Parsec SaaS',
    'Password',
  ]);
  const editButton = summaryContainer.locator('.summary-item-container').nth(0).locator('.summary-item__button');
  await expect(editButton).toBeVisible();
  await expect(editButton).toHaveText('Edit');
  await editButton.click();

  await expect(summaryContainer).toBeHidden();
  await expect(orgNameContainer).toBeVisible();
  await fillIonInput(orgNameContainer.locator('ion-input'), `${DEFAULT_ORGANIZATION_INFORMATION.name}2`);
  await orgNameNext.click();

  await authNext.click();

  await expect(summaryContainer).toBeVisible();
  await expect(orgNameContainer).toBeHidden();
  await expect(summaryContainer.locator('.summary-item__text')).toHaveText([
    `${DEFAULT_ORGANIZATION_INFORMATION.name}2`,
    DEFAULT_USER_INFORMATION.name,
    DEFAULT_USER_INFORMATION.email,
    'Parsec SaaS',
    'Password',
  ]);
  await expect(summaryNext).toBeTrulyEnabled();
});
