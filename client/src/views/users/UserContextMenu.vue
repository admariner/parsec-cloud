<!-- Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS -->

<template>
  <ion-content id="user-context-menu">
    <ion-list class="menu-list">
      <ion-item-group
        class="list-group"
        v-if="canRevoke"
      >
        <ion-item class="list-group-title button-small">
          <ion-text class="list-group-title__label">
            {{ $msTranslate('UsersPage.userContextMenu.titleRemove') }}
          </ion-text>
        </ion-item>

        <ion-item
          button
          @click="onClick(UserAction.Revoke)"
          class="ion-no-padding list-group-item"
        >
          <ion-icon
            class="list-group-item__icon"
            :icon="personRemove"
          />
          <ion-text class="body list-group-item__label">
            {{ $msTranslate({ key: 'UsersPage.userContextMenu.actionRevoke', count: multipleSelected ? 2 : 1 }) }}
          </ion-text>
        </ion-item>
      </ion-item-group>

      <ion-item-group
        class="list-group"
        v-if="canUpdateProfile"
      >
        <ion-item class="list-group-title button-small">
          <ion-text class="list-group-title__label">
            {{ $msTranslate('UsersPage.userContextMenu.titleUpdateProfile') }}
          </ion-text>
        </ion-item>
        <ion-item
          button
          @click="onClick(UserAction.UpdateProfile)"
          class="ion-no-padding list-group-item"
        >
          <ion-icon
            class="list-group-item__icon"
            :icon="repeat"
          />
          <ion-text class="body list-group-item__label">
            {{ $msTranslate({ key: 'UsersPage.userContextMenu.actionUpdateProfile', count: multipleSelected ? 2 : 1 }) }}
          </ion-text>
        </ion-item>
      </ion-item-group>

      <ion-item-group
        class="list-group"
        v-if="!multipleSelected"
      >
        <ion-item class="list-group-title button-small">
          <ion-text class="list-group-title__label">
            {{ $msTranslate('UsersPage.userContextMenu.titleDetails') }}
          </ion-text>
        </ion-item>
        <ion-item
          button
          @click="onClick(UserAction.Details)"
          class="ion-no-padding list-group-item"
        >
          <ion-icon
            class="list-group-item__icon"
            :icon="informationCircle"
          />
          <ion-text class="body list-group-item__label">
            {{ $msTranslate('UsersPage.userContextMenu.actionDetails') }}
          </ion-text>
        </ion-item>
      </ion-item-group>

      <ion-item-group
        class="list-group"
        v-if="!multipleSelected"
      >
        <ion-item class="list-group-title button-small">
          <ion-text class="list-group-title__label">
            {{ $msTranslate('UsersPage.userContextMenu.titleAssignRoles') }}
          </ion-text>
        </ion-item>
        <ion-item
          button
          @click="onClick(UserAction.AssignRoles)"
          class="ion-no-padding list-group-item"
        >
          <ion-icon
            class="list-group-item__icon"
            :icon="returnUpForward"
          />
          <ion-text class="body list-group-item__label">
            {{ $msTranslate('UsersPage.userContextMenu.actionAssignRoles') }}
          </ion-text>
        </ion-item>
      </ion-item-group>
    </ion-list>
  </ion-content>
</template>

<script setup lang="ts">
import { IonContent, IonIcon, IonItem, IonItemGroup, IonText, IonList, popoverController } from '@ionic/vue';
import { informationCircle, personRemove, returnUpForward, repeat } from 'ionicons/icons';
import { UserAction } from '@/views/users/types';

defineProps<{
  multipleSelected?: boolean;
  canUpdateProfile?: boolean;
  canRevoke?: boolean;
}>();

async function onClick(action: UserAction): Promise<boolean> {
  return popoverController.dismiss({ action: action });
}
</script>

<style lang="scss" scoped></style>
