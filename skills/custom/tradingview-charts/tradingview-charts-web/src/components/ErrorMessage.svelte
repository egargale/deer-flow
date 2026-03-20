<script lang="ts">
  export let message = '';
  export let type: 'error' | 'warning' = 'error';
  export let dismissible = true;

  let visible = true;

  function dismiss() {
    visible = false;
  }
</script>

{#if visible}
  <div class="alert alert-{type} mb-4" class:alert-dismissible={dismissible}>
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
      {#if type === 'error'}
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
      {:else}
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0zm-9 3.75h.008v.008H12v-.008z" />
      {/if}
    </svg>
    <span>{message}</span>
    {#if dismissible}
      <button on:click={dismiss} class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
    {/if}
  </div>
{/if}