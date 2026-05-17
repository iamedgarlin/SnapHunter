import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * Shared navigation state (in-memory only).
 *
 * Before this store, MapView held `navigatingId` / `routeInfo` as local
 * refs, so leaving the Map tab threw the active route away. Lifting it
 * to a Pinia store means the route survives switching tabs, and Home /
 * Tasks can show a "currently navigating" state with a red X to cancel,
 * without each view re-implementing it.
 *
 * This is intentionally NOT persisted to localStorage — a full page
 * reload clears it, which is the chosen behaviour. Only `cancel()`
 * ends navigation within a session; switching views never does.
 */
export const useNavigationStore = defineStore('navigation', () => {
  // The thing we are navigating to. `id` mirrors the marker id used by
  // MapView: `task-<id>` or `park-<id>` so every view can match its own
  // card against the active target.
  const target = ref(null)      // { id, name, lat, lng, kind: 'task' | 'park', seriesId? }
  const routeInfo = ref(null)   // { name, distance, duration, steps, arrived }

  const navigatingId = computed(() => target.value?.id ?? null)
  const isNavigating = computed(() => !!target.value)
  const arrived = computed(() => !!routeInfo.value?.arrived)

  // Kept as a no-op so views can call navStore.load() unconditionally on
  // mount without caring whether persistence exists. If persistence is
  // ever wanted again, only this function needs to change.
  function load() { /* in-memory store: nothing to restore */ }

  /**
   * Begin (or replace) an active navigation. Called by MapView once it
   * has a target; routeInfo is filled in slightly later when OSRM
   * responds, via setRouteInfo.
   */
  function start(t) {
    target.value = {
      id: t.id,
      name: t.name,
      lat: t.lat,
      lng: t.lng,
      kind: String(t.id).startsWith('task-') ? 'task' : 'park',
      seriesId: t.seriesId ?? null,
    }
    routeInfo.value = null
  }

  function setRouteInfo(info) {
    routeInfo.value = info
  }

  function markArrived() {
    if (routeInfo.value) {
      routeInfo.value = { ...routeInfo.value, arrived: true }
    }
  }

  /** The ONLY way navigation ends. Views call this from their red X. */
  function cancel() {
    target.value = null
    routeInfo.value = null
  }

  /** True when the given card id is the one currently being navigated. */
  function isActive(id) {
    return target.value?.id === id
  }

  return {
    target,
    routeInfo,
    navigatingId,
    isNavigating,
    arrived,
    load,
    start,
    setRouteInfo,
    markArrived,
    cancel,
    isActive,
  }
})