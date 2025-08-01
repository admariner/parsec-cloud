<!-- Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS -->

<template>
  <div class="login-popup">
    <!-- login -->
    <div class="login-header">
      <ion-text class="login-header__title title-h1">
        {{ $msTranslate('HomePage.organizationLogin.login') }}
      </ion-text>
    </div>
    <ion-card class="login-card">
      <ion-card-header class="login-card-header">
        <organization-card
          :device="device"
          :org-name-only="true"
        />
      </ion-card-header>
      <ion-card-content class="login-card-content">
        <ms-input
          :label="'HomePage.organizationLogin.emailLabel'"
          v-model="email"
          id="ms-input"
          :disabled="true"
        />
        <div class="login-card-content__password">
          <ms-password-input
            :label="'HomePage.organizationLogin.passwordLabel'"
            ref="passwordInput"
            v-model="password"
            @on-enter-keyup="onLoginClick()"
            id="password-input"
            @change="onPasswordChange"
            :error-message="errorMessage"
            :password-is-invalid="passwordIsInvalid"
          />
          <ion-button
            fill="clear"
            @click="$emit('forgottenPasswordClick', device)"
            id="forgotten-password-button"
            class="button-medium"
          >
            {{ $msTranslate('HomePage.organizationLogin.forgottenPassword') }}
          </ion-button>
        </div>
      </ion-card-content>
      <ion-footer class="login-card-footer">
        <ion-button
          @click="onLoginClick()"
          size="large"
          :disabled="password.length == 0 || loginInProgress === true"
          class="login-button"
        >
          <span v-show="!loginInProgress">{{ $msTranslate('HomePage.organizationLogin.loginButton') }}</span>
          <ms-spinner
            v-show="loginInProgress === true"
            :size="14"
            :speed="2"
          />
        </ion-button>
      </ion-footer>
    </ion-card>
    <!-- end of login -->
  </div>
</template>

<script setup lang="ts">
import { MsInput, MsPasswordInput, MsSpinner } from 'megashark-lib';
import OrganizationCard from '@/components/organizations/OrganizationCard.vue';
import { AccessStrategy, AvailableDevice, ClientStartError, ClientStartErrorTag, DeviceAccessStrategyPassword } from '@/parsec';
import { IonButton, IonCard, IonCardContent, IonCardHeader, IonFooter, IonText } from '@ionic/vue';
import { onMounted, ref, useTemplateRef } from 'vue';

const props = defineProps<{
  device: AvailableDevice;
  loginInProgress?: boolean;
}>();

const emits = defineEmits<{
  (e: 'loginClick', device: AvailableDevice, access: DeviceAccessStrategyPassword): void;
  (e: 'forgottenPasswordClick', device: AvailableDevice): void;
}>();

const passwordInputRef = useTemplateRef<InstanceType<typeof MsPasswordInput>>('passwordInput');
const password = ref('');
const errorMessage = ref('');
const passwordIsInvalid = ref(false);
const email = props.device.humanHandle.email;

onMounted(async () => {
  await passwordInputRef.value?.setFocus();
});

async function onLoginClick(): Promise<void> {
  if (!props.loginInProgress) {
    emits('loginClick', props.device, AccessStrategy.usePassword(props.device, password.value));
  }
}

async function setLoginError(error: ClientStartError): Promise<void> {
  switch (error.tag) {
    case ClientStartErrorTag.LoadDeviceDecryptionFailed:
      errorMessage.value = 'HomePage.organizationLogin.passwordError';
      break;
    case ClientStartErrorTag.LoadDeviceInvalidPath:
      window.electronAPI.log('warn', error.error);
      errorMessage.value = 'HomePage.organizationLogin.deviceNotFound';
      break;
    case ClientStartErrorTag.LoadDeviceInvalidData:
      window.electronAPI.log('warn', error.error);
      errorMessage.value = 'HomePage.organizationLogin.deviceInvalidData';
      break;
    case ClientStartErrorTag.DeviceUsedByAnotherProcess:
      errorMessage.value = 'HomePage.organizationLogin.deviceAlreadyUsed';
      break;
    case ClientStartErrorTag.Internal:
      window.electronAPI.log('warn', error.error);
      errorMessage.value = 'HomePage.organizationLogin.unknownError';
      break;
  }
  passwordIsInvalid.value = true;
}

async function onPasswordChange(value: string): Promise<void> {
  if (value.length === 0) {
    passwordIsInvalid.value = false;
  }
  errorMessage.value = '';
}

defineExpose({
  setLoginError,
});
</script>

<style lang="scss" scoped>
.login-popup {
  height: auto;
  width: 100%;
  max-width: 28rem;
  margin: 2rem auto;
  display: flex;
  gap: 1.5rem;
  flex-direction: column;
  align-items: center;
  box-shadow: none;

  @include ms.responsive-breakpoint('xl') {
    margin: 0 auto;
  }

  @include ms.responsive-breakpoint('sm') {
    margin: 0 auto;
  }

  .login-header__title {
    background: var(--parsec-color-light-gradient-background);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .login-card {
    background: var(--parsec-color-light-secondary-white);
    border: 1px solid var(--parsec-color-light-secondary-medium);
    padding: 2em;
    margin: 0;
    border-radius: var(--parsec-radius-12);
    box-shadow: none;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    width: 100%;
    transition: box-shadow 150ms ease-in-out;
    overflow-y: auto;

    @include ms.responsive-breakpoint('sm') {
      padding: 1.5rem;
    }

    &:has(.has-focus) {
      box-shadow: var(--parsec-shadow-light);
    }

    &-header {
      padding: 0;
    }

    &-content {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      padding: 0;

      &__password {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        margin: 0;
      }

      #password-input {
        margin: 0;
      }

      #forgotten-password-button {
        margin: 0;
        position: relative;
        width: fit-content;
        color: var(--parsec-color-light-secondary-grey);

        &::part(native) {
          --background-hover: none;
          padding: 0 0 0 2px;
        }

        &:hover {
          color: var(--parsec-color-light-secondary-text);
        }
      }
    }

    &-footer {
      padding: 0;
      width: 100%;
      display: flex;
      gap: 1.5rem;
      align-items: center;

      .login-button {
        width: 100%;
      }
    }
  }
}
</style>
