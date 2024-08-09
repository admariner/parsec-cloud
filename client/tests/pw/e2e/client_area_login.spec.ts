// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

import { expect } from '@tests/pw/helpers/assertions';
import { MockBms } from '@tests/pw/helpers/bms';
import { DEFAULT_ORGANIZATION_INFORMATION, DEFAULT_USER_INFORMATION } from '@tests/pw/helpers/data';
import { msTest } from '@tests/pw/helpers/fixtures';
import { answerQuestion, fillIonInput } from '@tests/pw/helpers/utils';

msTest('Log into the customer area', async ({ home }) => {
  await MockBms.mockLogin(home);
  await MockBms.mockUserRoute(home);
  await MockBms.mockListOrganizations(home);
  await MockBms.mockOrganizationStats(home);
  await MockBms.mockOrganizationStatus(home);
  await MockBms.mockBillingDetails(home);
  await MockBms.mockGetInvoices(home);

  const button = home.locator('.topbar-buttons').locator('#trigger-customer-area-button');
  await expect(button).toHaveText('Customer area');
  await button.click();
  await expect(home).toHaveURL(/.+\/home$/);
  await fillIonInput(home.locator('.input-container').nth(0).locator('ion-input'), DEFAULT_USER_INFORMATION.email);
  await fillIonInput(home.locator('.input-container').nth(1).locator('ion-input'), DEFAULT_USER_INFORMATION.password);
  await home.locator('.saas-login-button__item').click();
  await expect(home.locator('.header-content').locator('.header-title')).toHaveText('Dashboard');
  const logOutButton = home.locator('.header-content').locator('.custom-button').first();
  await expect(logOutButton).toHaveText('Log out');
  await logOutButton.click();
  await answerQuestion(home, true, {
    expectedTitleText: 'Log out',
    expectedQuestionText: 'Do you want to log out?',
    expectedPositiveText: 'Log out',
    expectedNegativeText: 'Stay connected',
  });
  await expect(home).toHaveURL(/.+\/home$/);
});

msTest('Log into the customer area failed', async ({ home }) => {
  await MockBms.mockLogin(home, { POST: { errors: { status: 401, attribute: 'email' } } });

  const button = home.locator('.topbar-buttons').locator('#trigger-customer-area-button');
  await expect(button).toHaveText('Customer area');
  await button.click();
  await expect(home).toHaveURL(/.+\/home$/);
  await fillIonInput(home.locator('.input-container').nth(0).locator('ion-input'), DEFAULT_USER_INFORMATION.email);
  await fillIonInput(home.locator('.input-container').nth(1).locator('ion-input'), 'invalid_password');
  await home.locator('.saas-login-button__item').click();
  const error = home.locator('.saas-login-container').locator('.login-button-error');
  await expect(error).toBeVisible();
  await expect(error).toHaveText('Cannot log in. Please check your email and password.');
});

msTest('Switch pages', async ({ clientArea }) => {
  const pages = [
    { button: 'Dashboard', title: 'Dashboard', url: 'dashboard' },
    { button: 'Statistics', title: 'Statistics', url: 'statistics' },
    { button: 'Invoices', title: 'Invoices', url: 'invoices' },
    { button: 'Billing method', title: 'Payment methods', url: 'payment-methods' },
    { button: 'Billing details', title: 'Billing details', url: 'billing-details' },
  ];

  const title = clientArea.locator('.header-content').locator('.header-title');
  await expect(clientArea).toHaveURL(/.+\/clientArea\\?(?:.*)$/);
  await expect(title).toHaveText('Dashboard');
  await expect(clientArea.locator('.sidebar-header').locator('.card-header-title')).toBeVisible();
  const menuButtons = clientArea.locator('.menu-client').locator('.menu-client-list').getByRole('listitem');
  const buttonTexts = pages.map((texts) => texts.button);
  await expect(menuButtons).toHaveText(buttonTexts);
  for (let i = 0; i < pages.length; i++) {
    await menuButtons.nth(i).click();
    await expect(title).toHaveText(pages[i].title);
    // eslint-disable-next-line max-len
    const urlMatch = `https?://[a-z:0-9.]+/clientArea\\?(?:organization=[a-f0-9-]+&)?(?:page=${pages[i].url})&?(?:organization=[a-f0-9-]+)?`;
    await expect(clientArea).toHaveURL(new RegExp(urlMatch));
  }
});

msTest('Switch org', async ({ clientArea }) => {
  const org1 = DEFAULT_ORGANIZATION_INFORMATION.name;
  const org2 = `${DEFAULT_ORGANIZATION_INFORMATION.name}-2`;

  const orgSwitchButton = clientArea.locator('.sidebar-header').locator('.card-header-title');
  await expect(orgSwitchButton).toHaveText(org1);
  const popover = clientArea.locator('.popover-switch');
  await expect(popover).toBeHidden();
  await orgSwitchButton.click();
  await expect(popover).toBeVisible();
  const orgs = popover.locator('.organization-list').getByRole('listitem');
  const orgNames = orgs.locator('.organization-name');
  await expect(orgNames).toHaveText([org1, org2, 'All organizations']);
  await expect(orgs.nth(0).locator('.organization-icon-current')).toBeVisible();
  await expect(orgs.nth(1).locator('.organization-icon-current')).toBeHidden();
  await expect(orgs.nth(2).locator('.organization-icon-current')).toBeHidden();
  // Click on backdrop, nothing should change
  await clientArea.locator('.backdrop-hide').click();
  await expect(orgSwitchButton).toHaveText(org1);

  await expect(popover).toBeHidden();
  await orgSwitchButton.click();
  await expect(popover).toBeVisible();
  await expect(orgNames).toHaveText([org1, org2, 'All organizations']);
  await expect(orgs.nth(0).locator('.organization-icon-current')).toBeVisible();
  await expect(orgs.nth(1).locator('.organization-icon-current')).toBeHidden();
  await expect(orgs.nth(2).locator('.organization-icon-current')).toBeHidden();
  // Click on second org, should switch
  await orgs.nth(1).click();
  await expect(popover).toBeHidden();
  await expect(orgSwitchButton).toHaveText(org2);

  await orgSwitchButton.click();
  await expect(popover).toBeVisible();
  await expect(orgNames).toHaveText([org1, org2, 'All organizations']);
  // Current one should be second one
  await expect(orgs.nth(0).locator('.organization-icon-current')).toBeHidden();
  await expect(orgs.nth(1).locator('.organization-icon-current')).toBeVisible();
  await expect(orgs.nth(2).locator('.organization-icon-current')).toBeHidden();
});

msTest('Open settings modal', async ({ clientArea }) => {
  const settingsButton = clientArea.locator('.header-content').locator('.custom-button').nth(1);
  const modal = clientArea.locator('.settings-modal');
  await expect(modal).toBeHidden();
  await settingsButton.click();
  await expect(modal).toBeVisible();
  await expect(modal.locator('.ms-modal-header__title')).toHaveText('Settings');
});
