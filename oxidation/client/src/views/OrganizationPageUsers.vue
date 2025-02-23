<!-- Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 (eventually AGPL-3.0) 2016-present Scille SAS -->

<template>
  <ion-page>
    <ion-content>
      <ion-toolbar>
        <ion-searchbar v-model="searchUsersAndPendingUsersInput" />
        <ion-buttons
          slot="primary"
        >
          <ion-button
            color="primary"
            fill="solid"
            v-if="!isPlatform('mobile')"
          >
            <ion-icon
              :icon="add"
            />
            <ion-label>{{ $t('OrganizationPage.OrganizationPageUsers.inviteUser') }}</ion-label>
          </ion-button>
          <ion-button
            fill="clear"
            @click="listView = !listView"
          >
            <ion-icon
              slot="icon-only"
              :icon="listView ? grid : list"
            />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
      <div v-if="listView">
        <ion-item-divider>
          {{ pendingUsersExampleData.length }} {{ $t('OrganizationPage.OrganizationPageUsers.pendingInvitations') }}
        </ion-item-divider>
        <table
          v-if="!isPlatform('mobile')"
          class="pending-users-table"
        >
          <tr
            v-for="pendingUser in filteredPendingUsers"
            :key="pendingUser.id"
          >
            <td class="pending-user-email">
              {{ pendingUser.email }}
            </td>
            <td>
              <ion-button
                color="danger"
                fill="clear"
              >
                <ion-icon
                  slot="start"
                  :icon="personRemove"
                  color="danger"
                />
                <ion-label color="danger">
                  {{ $t('OrganizationPage.OrganizationPageUsers.OrganizationPendingUserContextMenu.cancelInvitation') }}
                </ion-label>
              </ion-button>
            </td>
            <td>
              <ion-button
                color="primary"
                fill="solid"
              >
                <ion-icon
                  slot="start"
                  :icon="personAdd"
                />
                <ion-label>{{ $t('OrganizationPage.OrganizationPageUsers.OrganizationPendingUserContextMenu.greetUser') }}</ion-label>
              </ion-button>
            </td>
          </tr>
        </table>
        <mobile-item-list
          v-for="pendingUser in filteredPendingUsers"
          :key="pendingUser.id"
          item-type="pendingUser"
          :primary-label="pendingUser.email"
          secondary-label="Pending invitation"
          @click="openPendingUserActionSheet()"
          @contextmenu.prevent="openPendingUserActionSheet()"
          @trigger-action-sheet="openPendingUserActionSheet()"
        />
        <ion-item-divider>7 utilisateurs : 2 administrateurs, 3 membres, 2 invités.</ion-item-divider>
        <mobile-item-list
          v-for="user in filteredUsers"
          item-type="user"
          :primary-label="user.name"
          :secondary-label="user.profile"
          :third-label="user.email"
          :key="user.id"
          @click="openUserActionSheet()"
          @contextmenu.prevent="openUserActionSheet()"
          @trigger-action-sheet="openUserActionSheet()"
        />
      </div>
      <template
        v-else
      >
        <ion-item-divider>
          {{ pendingUsersExampleData.length }} {{ $t('OrganizationPage.OrganizationPageUsers.pendingInvitations') }}
        </ion-item-divider>
        <table
          v-if="!isPlatform('mobile')"
          class="pending-users-table"
        >
          <tr
            v-for="pendingUser in filteredPendingUsers"
            :key="pendingUser.id"
          >
            <td class="pending-user-email">
              {{ pendingUser.email }}
            </td>
            <td>
              <ion-button
                color="primary"
                fill="solid"
              >
                <ion-icon
                  slot="start"
                  :icon="personAdd"
                />
                <ion-label>{{ $t('OrganizationPage.OrganizationPageUsers.OrganizationPendingUserContextMenu.greetUser') }}</ion-label>
              </ion-button>
            </td>
            <td>
              <ion-button
                color="danger"
                fill="clear"
              >
                <ion-icon
                  slot="start"
                  :icon="personRemove"
                  color="danger"
                />
                <ion-label color="danger">
                  {{ $t('OrganizationPage.OrganizationPageUsers.OrganizationPendingUserContextMenu.cancelInvitation') }}
                </ion-label>
              </ion-button>
            </td>
          </tr>
        </table>
        <div
          v-if="isPlatform('mobile')"
          class="users-grid-container"
        >
          <item-grid
            v-for="pendingUser in filteredPendingUsers"
            item-type="pendingUser"
            :primary-label="pendingUser.email"
            secondary-label="Pending invitation"
            :key="pendingUser.id"
            @click="handlePendingUserContextMenu($event)"
            @contextmenu.prevent="handlePendingUserContextMenu($event)"
            @trigger-context-menu="openPendingUserContextMenu($event)"
            @trigger-action-sheet="openPendingUserActionSheet()"
          />
        </div>
        <ion-item-divider>7 utilisateurs : 2 administrateurs, 3 standard, 2 externes.</ion-item-divider>
        <div
          class="users-grid-container"
        >
          <item-grid
            v-for="user in filteredUsers"
            item-type="user"
            :primary-label="user.name"
            :secondary-label="user.profile"
            :key="user.id"
            @contextmenu.prevent="handleUserContextMenu($event)"
            @trigger-context-menu="openUserContextMenu($event)"
            @trigger-action-sheet="openUserActionSheet()"
          />
        </div>
      </template>
      <ion-fab
        v-if="isPlatform('mobile')"
        vertical="bottom"
        horizontal="end"
        slot="fixed"
      >
        <ion-fab-button>
          <ion-icon :icon="add" />
        </ion-fab-button>
      </ion-fab>
    </ion-content>
  </ion-page>
</template>

<script setup lang = "ts" >
import {
  IonLabel,
  IonButton,
  IonIcon,
  IonPage,
  IonItemDivider,
  IonContent,
  popoverController,
  actionSheetController,
  isPlatform,
  IonFab,
  IonFabButton,
  IonSearchbar,
  IonToolbar,
  IonButtons
} from '@ionic/vue';

import {
  add, ban, grid, informationCircle, list, personAdd, personRemove, help
} from 'ionicons/icons';
import ItemGrid from '@/components/ItemGrid.vue';
import MobileItemList from '@/components/MobileItemList.vue';
import OrganizationPendingUserContextMenu from '@/components/OrganizationPendingUserContextMenu.vue';
import OrganizationUserContextMenu from '@/components/OrganizationUserContextMenu.vue';
import { useI18n } from 'vue-i18n';
import { ref, computed } from 'vue';

const { t } = useI18n();
const listView = ref(false);

const usersExampleData = [
  {
    'id': 345,
    'name': 'Jean Paul',
    'email': 'jean.paul@test.test',
    'profile': 'Administrator'
  },
  {
    'id': 456,
    'name': 'Alice Dupont',
    'email': 'alicedupont@test.test',
    'profile': 'Standard'
  },
  {
    'id': 567,
    'name': 'Alexandre Dubois long name test',
    'email': 'alexandre.dubois@secondtest.test.test.test',
    'profile': 'Standard'
  },
  {
    'id': 678,
    'name': 'Jean Martin',
    'email': 'jean.martin@thirdtest.test',
    'profile': 'Administrator'
  },
  {
    'id': 789,
    'name': 'Pierre Martin',
    'email': 'pierremartin@test.test',
    'profile': 'Standard'
  },
  {
    'id': 901,
    'name': 'Guillaume Dupont',
    'email': 'guillaume.dupont@dupont.test',
    'profile': 'Standard'
  },
  {
    'id': 102,
    'name': 'Clara Dubois',
    'email': 'clara.dubois@dubois.test',
    'profile': 'Standard'
  }
];

const pendingUsersExampleData = [
  {
    'id': 344,
    'email': 'christophe.dupont@hote.fr'
  },
  {
    'id': 455,
    'email': 'thomas.dupont@test.test'
  }
];

function handlePendingUserContextMenu(ev: Event): void {
  if (isPlatform('mobile')) { // @contextmenu event is triggered by a long press on mobile
    openPendingUserActionSheet();
  } else {
    openPendingUserContextMenu(ev);
  }
}

function handleUserContextMenu(ev: Event): void {
  if (isPlatform('mobile')) {
    openUserActionSheet();
  } else {
    openUserContextMenu(ev);
  }
}

async function openPendingUserContextMenu(ev: Event): Promise<void> {
  const popover = await popoverController
    .create({
      component: OrganizationPendingUserContextMenu,
      event: ev,
      translucent: true,
      showBackdrop: false,
      dismissOnSelect: true,
      reference: 'event'
    });
  await popover.present();

  const { role } = await popover.onDidDismiss();
  console.log('onDidDismiss resolved with role', role);
}

async function openUserContextMenu(ev: Event): Promise<void> {
  const popover = await popoverController
    .create({
      component: OrganizationUserContextMenu,
      event: ev,
      translucent: true,
      showBackdrop: false,
      dismissOnSelect: true,
      reference: 'event'
    });
  await popover.present();

  const { role } = await popover.onDidDismiss();
  console.log('onDidDismiss resolved with role', role);
}

async function openPendingUserActionSheet(): Promise<void> {
  const actionSheet = await actionSheetController
    .create({
      header: 'User name',
      buttons: [
        {
          text: t('OrganizationPage.OrganizationPageUsers.OrganizationPendingUserContextMenu.greetUser'),
          icon: personAdd,
          handler: (): void => {
            console.log('Greet clicked');
          }
        },
        {
          text: t('OrganizationPage.OrganizationPageUsers.OrganizationPendingUserContextMenu.cancelInvitation'),
          role: 'destructive',
          icon: personRemove,
          handler: (): void => {
            console.log('Cancel invitation clicked');
          }
        }
      ]
    });
  await actionSheet.present();
  const { role, data } = await actionSheet.onDidDismiss();
  console.log('onDidDismiss resolved with role and data: ', role, data);
}

async function openUserActionSheet(): Promise<void> {
  const actionSheet = await actionSheetController
    .create({
      header: 'User name',
      buttons: [
        {
          text: t('OrganizationPage.OrganizationPageUsers.OrganizationUserContextMenu.details'),
          icon: informationCircle,
          handler: (): void => {
            console.log('Details clicked');
          }
        },
        {
          text: t('OrganizationPage.OrganizationPageUsers.OrganizationUserContextMenu.revoke'),
          role: 'destructive',
          icon: ban,
          handler: (): void => {
            console.log('Revoke clicked');
          }
        }
      ]
    });
  await actionSheet.present();
  const { role, data } = await actionSheet.onDidDismiss();
  console.log('onDidDismiss resolved with role and data: ', role, data);
}

const searchUsersAndPendingUsersInput = ref('');

const filteredUsers = computed(() => {
  if (searchUsersAndPendingUsersInput.value !== '') {
    return usersExampleData.filter((user) => {
      return (user.email.toLowerCase().includes(
        searchUsersAndPendingUsersInput.value.toLowerCase()
      ) || user.name.toLowerCase().includes(
        searchUsersAndPendingUsersInput.value.toLowerCase()
      ));
    });
  } else {
    return usersExampleData;
  }
});

const filteredPendingUsers = computed(() => {
  if (searchUsersAndPendingUsersInput.value !== '') {
    return pendingUsersExampleData.filter((pendingUser) => {
      return pendingUser.email.toLowerCase().includes(
        searchUsersAndPendingUsersInput.value.toLowerCase()
      );
    });
  } else {
    return pendingUsersExampleData;
  }
});
</script>

<style lang="scss" scoped>
.users-grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
}

.pending-users-table {
    table-layout: auto;
    width: 100%;
}

.pending-users-table td:nth-last-child(-n+2) {
    text-align: end;
    width: 1%;
}

.pending-users-table td:nth-child(1) {
    padding-left: 16px;
}

.pending-user-email {
    word-break: break-word;
}
</style>
