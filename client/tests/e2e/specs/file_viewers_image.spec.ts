// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

import { expect, fillIonInput, msTest, openFileType, testFileViewerZoomLevel } from '@tests/e2e/helpers';

msTest('Image viewer', async ({ documents }) => {
  await openFileType(documents, 'png');
  await expect(documents).toBeViewerPage();
  await expect(documents).toHavePageTitle('File viewer');
  await expect(documents.locator('.file-viewer').locator('.file-viewer-topbar').locator('ion-text')).toHaveText(/^File_[a-z0-9_]+\.png$/);

  const wrapper = documents.locator('.file-viewer-wrapper');
  await expect(wrapper.locator('img')).toBeVisible();
  const bottomBar = documents.locator('.file-viewer-bottombar');
  const zoom = bottomBar.locator('.zoom-controls');
  await expect(zoom).toHaveCount(1);
});

msTest('Image viewer zoom', async ({ documents }) => {
  await openFileType(documents, 'png');
  await expect(documents).toBeViewerPage();
  await expect(documents).toHavePageTitle('File viewer');
  await expect(documents.locator('.file-viewer').locator('.file-viewer-topbar').locator('ion-text')).toHaveText(/^File_[a-z0-9_]+\.png$/);
  const bottomBar = documents.locator('.file-viewer-bottombar');
  const wrapper = documents.locator('.file-viewer-wrapper');
  const zoom = bottomBar.locator('.zoom-controls');
  const zoomReset = bottomBar.locator('#reset-zoom');
  const zoomOut = zoom.locator('.file-controls-button-container').nth(0);
  const zoomIn = zoom.locator('.file-controls-button-container').nth(1);
  const zoomLevel = zoom.locator('ion-text.zoom-level-input');
  const zoomLevelInput = zoom.locator('ion-input.zoom-level-input');

  await expect(zoomLevelInput).toBeHidden();

  await expect(zoomLevel).toHaveText('100 %');
  await testFileViewerZoomLevel(wrapper, '1');

  await zoomOut.click();
  await zoomOut.click();
  await expect(zoomLevel).toHaveText('80 %');
  await testFileViewerZoomLevel(wrapper, '0.8');
  for (let i = 0; i < 8; i++) {
    await zoomOut.click();
  }
  await expect(zoomLevel).toHaveText('5 %');
  await expect(zoomOut).toBeTrulyDisabled();
  await testFileViewerZoomLevel(wrapper, '0.05');
  await zoomReset.click();
  await expect(zoomLevel).toHaveText('100 %');
  await testFileViewerZoomLevel(wrapper, '1');
  await expect(zoomOut).toBeTrulyEnabled();

  await zoomIn.click();
  await zoomIn.click();
  await expect(zoomLevel).toHaveText('150 %');
  await testFileViewerZoomLevel(wrapper, '1.5');
  for (let i = 0; i < 6; i++) {
    await zoomIn.click();
  }
  await expect(zoomIn).toBeTrulyDisabled();
  await expect(zoomLevel).toHaveText('500 %');
  await testFileViewerZoomLevel(wrapper, '5');
  await zoomReset.click();

  await expect(zoomLevel).toHaveText('100 %');
  await testFileViewerZoomLevel(wrapper, '1');
  await expect(zoomIn).toBeTrulyEnabled();

  await zoomLevel.click();
  await expect(zoomLevel).toBeHidden();
  await expect(zoomLevelInput).toBeVisible();
  await fillIonInput(zoomLevelInput, '42');
  await expect(zoomLevel).toHaveText('40 %');
  await testFileViewerZoomLevel(wrapper, '0.4');
});
