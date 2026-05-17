<template>
  <div class="min-h-full pb-6" style="background: #f0fdf4; font-family: var(--font-game)">

    <!-- Header -->
    <div class="relative overflow-hidden px-4 pt-6 pb-5"
      style="background: linear-gradient(160deg, #bbf7d0, #6ee7b7); border-radius: 0 0 32px 32px; border-bottom: 4px solid #34d399">
      <h1 class="text-2xl font-black text-emerald-900">Series Gallery</h1>
      <p class="text-xs font-bold text-emerald-700 mt-1">Complete a series to unlock a badge!</p>
    </div>

    <div class="px-4 flex flex-col gap-4 mt-4 pb-4">

      <!-- ═══ Parks Series (always first) ═══ -->
      <div class="rounded-3xl overflow-hidden"
        :style="`border: 2.5px solid ${parksSeries.borderColor}; border-bottom: 5px solid ${parksSeries.borderBottomColor}`">

        <!-- Card header -->
        <div class="px-4 pt-4 pb-3 flex items-center justify-between"
          :style="`background: ${parksSeries.iconBg}`">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-2xl flex items-center justify-center"
              style="background: white; border-bottom: 3px solid"
              :style="`border-color: ${parksSeries.borderColor}; border-bottom-color: ${parksSeries.borderBottomColor}`">
              <component :is="parksSeries.icon" :size="26" weight="duotone" :color="parksSeries.color" />
            </div>
            <div>
              <div class="flex items-center gap-1.5">
                <p class="text-base font-black" :style="`color: ${parksSeries.color}`">{{ parksSeries.name }}</p>
                <PhSeal v-if="parksSeriesCompleted" :size="16" weight="duotone" color="#f59e0b" />
              </div>
              <p class="text-xs font-semibold text-gray-500">{{ parksSeries.description }}</p>
            </div>
          </div>
          <div class="flex flex-col items-end gap-0.5">
            <span class="text-sm font-black" :style="`color: ${parksSeries.color}`">
              {{ parksDoneCount }}/{{ parkCards.length }}
            </span>
          </div>
        </div>

        <!-- Progress bar -->
        <div class="px-4 py-2" :style="`background: ${parksSeries.iconBg}`">
          <div class="h-2.5 rounded-full overflow-hidden"
            style="background: rgba(255,255,255,0.6)">
            <div class="h-full rounded-full transition-all duration-500"
              :style="`width: ${parksProgress}%; background: ${parksSeries.color}`">
            </div>
          </div>
        </div>

        <!-- Dashed separator (stamp perforation effect) -->
        <div class="flex items-center px-2" :style="`background: ${parksSeries.iconBg}`">
          <div class="flex-1 border-t-2 border-dashed" :style="`border-color: ${parksSeries.borderColor}`"></div>
          <div class="mx-2">
            <PhMedal :size="18" weight="duotone"
              :color="parksSeriesCompleted ? '#f59e0b' : parksSeries.borderColor" />
          </div>
          <div class="flex-1 border-t-2 border-dashed" :style="`border-color: ${parksSeries.borderColor}`"></div>
        </div>

        <!-- Park cards horizontal scroll -->
        <div class="bg-white px-4 pt-3 pb-4">
          <div v-if="parksLoading && !parkCards.length"
            class="flex items-center justify-center py-6 gap-2">
            <PhSpinner :size="20" weight="duotone" color="#10b981" class="animate-spin" />
            <span class="text-xs font-bold text-gray-400">Finding parks near you...</span>
          </div>
          <div v-else-if="!parkCards.length"
            class="flex items-center justify-center py-6 text-xs font-semibold text-gray-400">
            No parks found nearby
          </div>
          <div v-else class="flex gap-3 overflow-x-auto pb-1"
            style="scrollbar-width: none; -ms-overflow-style: none;">

            <div v-for="park in sortedParkCards" :key="park.parkId"
              class="flex-shrink-0 flex flex-col rounded-2xl cursor-pointer active:scale-95 transition-all overflow-hidden relative"
              style="width: 140px; height: 160px;"
              :style="navStore.isActive(parkCardNavId(park))
                ? `background: ${parksSeries.iconBg}; border: 2px solid ${navStore.arrived ? parksSeries.borderColor : '#fecaca'}; border-bottom: 3px solid ${navStore.arrived ? parksSeries.borderBottomColor : '#f87171'}`
                : park.done
                  ? `background: ${parksSeries.iconBg}; border: 2px solid ${parksSeries.borderColor}; border-bottom: 3px solid ${parksSeries.borderBottomColor}`
                  : 'background: #f8fafc; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'"
              @click="navStore.isActive(parkCardNavId(park)) ? cancelNavigation() : openParkModal(park)">

              <!-- Navigating / Visited badge -->
              <div v-if="navStore.isActive(parkCardNavId(park))"
                class="absolute top-2 right-2 flex items-center gap-0.5 px-1.5 py-0.5 rounded-full"
                :style="navStore.arrived
                  ? `background: ${parksSeries.color}; color: white`
                  : 'background: #ef4444; color: white'">
                <PhNavigationArrow :size="10" weight="duotone" color="white" />
                <span class="text-xs font-black" style="font-size: 10px; line-height: 1">{{ navStore.arrived ? 'Arrived' : 'Navigating' }}</span>
              </div>
              <div v-else-if="park.done"
                class="absolute top-2 right-2 flex items-center gap-0.5 px-1.5 py-0.5 rounded-full"
                :style="`background: ${parksSeries.color}; color: white`">
                <PhCheckCircle :size="10" weight="duotone" color="white" />
                <span class="text-xs font-black" style="font-size: 10px; line-height: 1">Visited</span>
              </div>

              <!-- Icon area -->
              <div class="flex items-center justify-center pt-3 pb-2">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                  :style="park.done || navStore.isActive(parkCardNavId(park))
                    ? `background: white; border: 2px solid ${parksSeries.borderColor}`
                    : 'background: white; border: 2px solid #e2e8f0'">
                  <PhTree :size="20" weight="duotone"
                    :color="park.done || navStore.isActive(parkCardNavId(park)) ? parksSeries.color : '#94a3b8'" />
                </div>
              </div>

              <!-- Park name -->
              <div class="px-3 flex-1 flex flex-col justify-between pb-3">
                <div>
                  <p class="text-xs font-black leading-tight overflow-hidden"
                    style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;"
                    :style="park.done || navStore.isActive(parkCardNavId(park)) ? `color: ${parksSeries.color}` : 'color: #1f2937'">
                    {{ park.parkName }}
                  </p>
                  <p class="text-xs font-semibold text-gray-400 mt-1">
                    {{ parkSizeShort(park.parkHa) }} ·
                    {{ park.distance != null
                      ? (park.distance < 1000
                          ? Math.round(park.distance) + 'm'
                          : (park.distance / 1000).toFixed(1) + 'km')
                      : '' }}
                  </p>
                </div>
                <div class="flex items-center justify-between mt-2">
                  <div class="flex items-center gap-0.5">
                    <PhLightning :size="11" weight="duotone" color="#f59e0b" />
                    <span class="text-xs font-black text-amber-500">+50</span>
                  </div>
                  <!-- Active: red X (or check on arrival) to cancel -->
                  <div v-if="navStore.isActive(parkCardNavId(park))"
                    class="w-6 h-6 rounded-lg flex items-center justify-center"
                    :style="navStore.arrived
                      ? 'background:#f0fdf4;border:1.5px solid #bbf7d0'
                      : 'background:#fef2f2;border:1.5px solid #fecaca'">
                    <PhCheck v-if="navStore.arrived" :size="13" weight="bold" color="#16a34a" />
                    <PhX v-else :size="13" weight="bold" color="#ef4444" />
                  </div>
                  <PhCheckCircle v-else-if="park.done" :size="16" weight="duotone" :color="parksSeries.color" />
                  <PhNavigationArrow v-else :size="14" weight="duotone" color="#cbd5e1" />
                </div>
              </div>
            </div>

            <!-- Badge unlock card -->
            <div class="flex-shrink-0 flex flex-col items-center justify-center gap-2 rounded-2xl"
              style="width: 100px; height: 160px; border: 2px dashed #e2e8f0; background: #f8fafc">
              <PhMedal :size="28" weight="duotone"
                :color="parksSeriesCompleted ? '#f59e0b' : '#cbd5e1'" />
              <p class="text-xs font-black text-center px-2 leading-tight"
                :style="parksSeriesCompleted ? 'color: #f59e0b' : 'color: #94a3b8'">
                {{ parksSeriesCompleted ? 'All explored!' : 'Visit them all!' }}
              </p>
            </div>
          </div>
        </div>

      </div>

      <div v-if="loadingTasks" class="flex items-center justify-center py-12 gap-2">
        <PhSpinner :size="24" weight="duotone" color="#10b981" class="animate-spin" />
        <span class="text-sm font-bold text-gray-400">Loading series...</span>
      </div>

      <!-- Series cards (stamp style) -->
      <div v-else v-for="series in seriesList" :key="series.id"
        class="rounded-3xl overflow-hidden"
        :style="`border: 2.5px solid ${series.borderColor}; border-bottom: 5px solid ${series.borderBottomColor}`">

        <!-- Card header -->
        <div class="px-4 pt-4 pb-3 flex items-center justify-between"
          :style="`background: ${series.iconBg}`">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-2xl flex items-center justify-center"
              style="background: white; border-bottom: 3px solid"
              :style="`border-color: ${series.borderColor}; border-bottom-color: ${series.borderBottomColor}`">
              <component :is="series.icon" :size="26" weight="duotone" :color="series.color" />
            </div>
            <div>
              <div class="flex items-center gap-1.5">
                <p class="text-base font-black" :style="`color: ${series.color}`">{{ series.name }}</p>
                <PhSeal v-if="seriesCompleted(series.id)" :size="16" weight="duotone" color="#f59e0b" />
              </div>
              <p class="text-xs font-semibold text-gray-500">{{ series.description }}</p>
            </div>
          </div>
          <div class="flex flex-col items-end gap-0.5">
            <span class="text-sm font-black" :style="`color: ${series.color}`">
              {{ seriesCompletedCount(series.id) }}/{{ getSeriesTasks(series.id).length }}
            </span>
          </div>
        </div>

        <!-- Progress bar -->
        <div class="px-4 py-2" :style="`background: ${series.iconBg}`">
          <div class="h-2.5 rounded-full overflow-hidden"
            style="background: rgba(255,255,255,0.6)">
            <div class="h-full rounded-full transition-all duration-500"
              :style="`width: ${seriesProgress(series.id)}%; background: ${series.color}`">
            </div>
          </div>
        </div>

        <!-- Dashed separator (stamp perforation effect) -->
        <div class="flex items-center px-2" :style="`background: ${series.iconBg}`">
          <div class="flex-1 border-t-2 border-dashed" :style="`border-color: ${series.borderColor}`"></div>
          <div class="mx-2">
            <PhMedal :size="18" weight="duotone"
              :color="seriesCompleted(series.id) ? '#f59e0b' : series.borderColor" />
          </div>
          <div class="flex-1 border-t-2 border-dashed" :style="`border-color: ${series.borderColor}`"></div>
        </div>

        <!-- Task cards horizontal scroll -->
        <div class="bg-white px-4 pt-3 pb-4">
          <div v-if="!getGroupedTasks(series.id).length"
            class="flex items-center justify-center py-6 text-xs font-semibold text-gray-400">
            No tasks loaded yet
          </div>
          <div v-else class="flex gap-3 overflow-x-auto pb-1"
            style="scrollbar-width: none; -ms-overflow-style: none;">

            <div v-for="group in getSortedGroupedTasks(series.id)" :key="group.key"
              class="flex-shrink-0 flex flex-col rounded-2xl cursor-pointer active:scale-95 transition-all overflow-hidden relative"
              style="width: 140px; height: 160px;"
              :style="groupNavId(group)
                ? `background: ${series.iconBg}; border: 2px solid ${navStore.arrived ? series.borderColor : '#fecaca'}; border-bottom: 3px solid ${navStore.arrived ? series.borderBottomColor : '#f87171'}`
                : group.allDone
                  ? `background: ${series.iconBg}; border: 2px solid ${series.borderColor}; border-bottom: 3px solid ${series.borderBottomColor}`
                  : 'background: #f8fafc; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'"
              @click="groupNavId(group) ? cancelNavigation() : handleCardClick(group, series)">

              <!-- Navigating badge takes precedence over the multi-location one -->
              <div v-if="groupNavId(group)"
                class="absolute top-2 right-2 flex items-center gap-0.5 px-1.5 py-0.5 rounded-full"
                :style="navStore.arrived ? `background: ${series.color}; color: white` : 'background: #ef4444; color: white'">
                <PhNavigationArrow :size="10" weight="duotone" color="white" />
                <span class="text-xs font-black" style="font-size: 10px; line-height: 1">{{ navStore.arrived ? 'Arrived' : 'Navigating' }}</span>
              </div>
              <div v-else-if="group.tasks.length > 1"
                class="absolute top-2 right-2 flex items-center gap-0.5 px-1.5 py-0.5 rounded-full"
                :style="group.allDone
                  ? `background: ${series.color}; color: white`
                  : 'background: #e2e8f0; color: #64748b'">
                <PhMapPin :size="10" weight="duotone" :color="group.allDone ? 'white' : '#64748b'" />
                <span class="text-xs font-black" style="font-size: 10px; line-height: 1">{{ group.doneCount }}/{{ group.tasks.length }}</span>
              </div>

              <!-- Icon area -->
              <div class="flex items-center justify-center pt-3 pb-2">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                  :style="group.allDone || groupNavId(group)
                    ? `background: white; border: 2px solid ${series.borderColor}`
                    : 'background: white; border: 2px solid #e2e8f0'">
                  <PhCamera :size="20" weight="duotone"
                    :color="group.allDone || groupNavId(group) ? series.color : '#94a3b8'" />
                </div>
              </div>

              <!-- Task name -->
              <div class="px-3 flex-1 flex flex-col justify-between pb-3">
                <div>
                  <p class="text-xs font-black leading-tight overflow-hidden"
                    style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;"
                    :style="group.allDone || groupNavId(group) ? `color: ${series.color}` : 'color: #1f2937'">
                    {{ group.taskName }}
                  </p>
                  <p v-if="group.tasks.length === 1" class="text-xs font-semibold text-gray-400 mt-1 overflow-hidden"
                    style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">
                    {{ group.tasks[0].taskDescription }}
                  </p>
                  <p v-else class="text-xs font-semibold mt-1"
                    :style="group.someDone ? `color: ${series.color}` : 'color: #94a3b8'">
                    {{ group.tasks.length }} locations
                  </p>
                </div>
                <div class="flex items-center justify-between mt-2">
                  <div class="flex items-center gap-0.5">
                    <PhLightning :size="11" weight="duotone" color="#f59e0b" />
                    <span class="text-xs font-black text-amber-500">+{{ group.totalReward }}</span>
                  </div>
                  <!-- Active: red X (or check on arrival) to cancel -->
                  <div v-if="groupNavId(group)"
                    class="w-6 h-6 rounded-lg flex items-center justify-center"
                    :style="navStore.arrived
                      ? 'background:#f0fdf4;border:1.5px solid #bbf7d0'
                      : 'background:#fef2f2;border:1.5px solid #fecaca'">
                    <PhCheck v-if="navStore.arrived" :size="13" weight="bold" color="#16a34a" />
                    <PhX v-else :size="13" weight="bold" color="#ef4444" />
                  </div>
                  <PhCheckCircle v-else-if="group.allDone" :size="16" weight="duotone" :color="series.color" />
                  <PhCamera v-else :size="14" weight="duotone" color="#cbd5e1" />
                </div>
              </div>
            </div>

            <!-- Badge unlock card -->
            <div class="flex-shrink-0 flex flex-col items-center justify-center gap-2 rounded-2xl"
              style="width: 100px; height: 160px; border: 2px dashed #e2e8f0; background: #f8fafc">
              <PhMedal :size="28" weight="duotone"
                :color="seriesCompleted(series.id) ? '#f59e0b' : '#cbd5e1'" />
              <p class="text-xs font-black text-center px-2 leading-tight"
                :style="seriesCompleted(series.id) ? 'color: #f59e0b' : 'color: #94a3b8'">
                {{ seriesCompleted(series.id) ? 'Badge unlocked!' : 'Complete all!' }}
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Hidden file input -->
    <input ref="fileInput" type="file" accept="image/*" capture="environment"
      class="hidden" @change="handlePhotoCapture" />

    <!-- Location picker modal (for grouped tasks with multiple locations) -->
    <div v-if="showLocationPicker"
      class="fixed inset-0 flex items-end justify-center z-50"
      style="background: rgba(0,0,0,0.4)"
      @click.self="closeLocationPicker">
      <div class="w-full max-w-md bg-white rounded-t-3xl p-6 flex flex-col gap-3"
        :style="`border-top: 4px solid ${selectedSeries?.borderBottomColor || '#34d399'}`">

        <!-- Header -->
        <div class="flex items-center gap-3 mb-1">
          <div class="w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0"
            :style="`background: ${selectedSeries?.iconBg}; border: 2px solid ${selectedSeries?.borderColor}; border-bottom: 3px solid ${selectedSeries?.borderBottomColor}`">
            <component :is="selectedSeries?.icon" :size="24" weight="duotone" :color="selectedSeries?.color || '#16a34a'" />
          </div>
          <div>
            <p class="text-lg font-black text-gray-800">{{ selectedGroup?.taskName }}</p>
            <p class="text-xs font-semibold text-gray-400">
              {{ selectedGroup?.doneCount }}/{{ selectedGroup?.tasks.length }} locations completed
            </p>
          </div>
        </div>

        <!-- Location progress bar -->
        <div class="h-2 rounded-full overflow-hidden" style="background: #f1f5f9">
          <div class="h-full rounded-full transition-all duration-500"
            :style="`width: ${selectedGroup ? Math.round((selectedGroup.doneCount / selectedGroup.tasks.length) * 100) : 0}%; background: ${selectedSeries?.color}`">
          </div>
        </div>

        <!-- Task list -->
        <div class="flex flex-col gap-2 max-h-64 overflow-y-auto" style="scrollbar-width: thin">
          <div v-for="task in selectedGroup?.tasks" :key="task.taskId"
            class="flex items-center gap-3 p-3 rounded-2xl cursor-pointer active:scale-98 transition-all"
            :style="task.done
              ? `background: ${selectedSeries?.iconBg}; border: 2px solid ${selectedSeries?.borderColor}`
              : 'background: #f8fafc; border: 2px solid #e2e8f0'"
            @click="openConfirmFromLocation(task)">

            <!-- Status icon -->
            <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
              :style="task.done
                ? `background: ${selectedSeries?.color}`
                : 'background: white; border: 2px solid #e2e8f0'">
              <PhCheckCircle v-if="task.done" :size="18" weight="duotone" color="white" />
              <PhMapPin v-else :size="18" weight="duotone" color="#94a3b8" />
            </div>

            <!-- Task info -->
            <div class="flex-1 min-w-0">
              <p class="text-sm font-black leading-tight"
                :style="task.done ? `color: ${selectedSeries?.color}` : 'color: #1f2937'">
                {{ task.taskDescription }}
              </p>
            </div>

            <!-- Reward + Navigate -->
            <div class="flex items-center gap-1.5 flex-shrink-0">
              <div class="flex items-center gap-0.5">
                <PhLightning :size="12" weight="duotone" color="#f59e0b" />
                <span class="text-xs font-black text-amber-500">+{{ task.rewardPoint }}</span>
              </div>
              <button v-if="!task.done && task.latitude != null"
                class="w-7 h-7 rounded-lg flex items-center justify-center"
                style="background: #eff6ff; border: 1.5px solid #bfdbfe; border-bottom: 2px solid #93c5fd"
                @click.stop="goNavigate(task)">
                <PhNavigationArrow :size="13" weight="duotone" color="#3b82f6" />
              </button>
              <PhCaretRight v-if="!task.done" :size="14" weight="bold" color="#cbd5e1" />
            </div>
          </div>
        </div>

        <button class="text-sm font-bold text-gray-400 py-2" @click="closeLocationPicker">
          Close
        </button>
      </div>
    </div>

    <!-- Task detail + confirm modal -->
    <div v-if="showModal"
      class="fixed inset-0 flex items-end justify-center z-50"
      style="background: rgba(0,0,0,0.4)"
      @click.self="closeConfirm">
      <div class="w-full max-w-md bg-white rounded-t-3xl p-6 flex flex-col gap-4"
        :style="`border-top: 4px solid ${selectedSeries?.borderBottomColor || '#34d399'}`">

        <div class="flex items-start gap-3">
          <div class="w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0"
            :style="`background: ${selectedSeries?.iconBg}; border: 2px solid ${selectedSeries?.borderColor}; border-bottom: 3px solid ${selectedSeries?.borderBottomColor}`">
            <PhCamera :size="28" weight="duotone" :color="selectedSeries?.color || '#16a34a'" />
          </div>
          <div class="flex-1">
            <p class="text-lg font-black text-gray-800">{{ selectedTask?.taskName }}</p>
            <p class="text-xs font-semibold text-gray-400 mt-0.5 leading-relaxed">{{ selectedTask?.taskDescription }}</p>
          </div>
        </div>

        <div v-if="capturedPhoto"
          class="w-full rounded-2xl overflow-hidden"
          style="border: 2px solid #bbf7d0; border-bottom: 3px solid #34d399">
          <img :src="capturedPhoto" class="w-full object-cover" style="max-height: 200px" />
        </div>

        <div v-if="evaluating" class="flex items-center justify-center gap-2 py-2">
          <PhSpinner :size="20" weight="duotone" color="#10b981" class="animate-spin" />
          <span class="text-sm font-bold text-gray-400">Checking your photo...</span>
        </div>

        <div v-if="evalResult" class="rounded-2xl p-3"
          :style="evalResult.matched
            ? 'background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #34d399'
            : 'background: #fef2f2; border: 2px solid #fecaca; border-bottom: 3px solid #f87171'">
          <div class="flex items-center gap-2 mb-1">
            <PhCheckCircle v-if="evalResult.matched" :size="18" weight="duotone" color="#16a34a" />
            <PhXCircle v-else :size="18" weight="duotone" color="#ef4444" />
            <p class="text-sm font-black"
              :style="evalResult.matched ? 'color: #16a34a' : 'color: #ef4444'">
              {{ evalResult.matched ? 'Task complete!' : 'Not quite right...' }}
            </p>
          </div>
          <p class="text-xs font-semibold text-gray-500">{{ evalResult.reason }}</p>
        </div>

        <div class="bg-amber-50 rounded-2xl p-3 flex items-center gap-2"
          style="border: 2px solid #fde68a; border-bottom: 3px solid #fbbf24">
          <PhLightning :size="20" weight="duotone" color="#f59e0b" />
          <p class="text-sm font-black text-amber-700">
            Complete this task to earn +{{ selectedTask?.rewardPoint }} XP!
          </p>
        </div>

        <!-- Location status banner -->
        <div v-if="selectedTask?.latitude != null" class="rounded-2xl p-3 flex items-center gap-2"
          :style="locationStatus === 'in_range'
            ? 'background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #34d399'
            : locationStatus === 'checking'
              ? 'background: #f8fafc; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'
              : 'background: #fff7ed; border: 2px solid #fed7aa; border-bottom: 3px solid #fdba74'">
          <PhSpinner v-if="locationStatus === 'checking'" :size="16" weight="duotone" color="#94a3b8" class="animate-spin" />
          <PhMapPin v-else-if="locationStatus === 'in_range'" :size="16" weight="duotone" color="#16a34a" />
          <PhWarning v-else :size="16" weight="duotone" color="#f59e0b" />
          <p class="text-xs font-bold" :style="locationStatus === 'in_range' ? 'color: #16a34a' : locationStatus === 'checking' ? 'color: #94a3b8' : 'color: #ea580c'">
            {{ locationMessage }}
          </p>
        </div>

        <!-- Navigate to task location -->
        <button v-if="selectedTask?.latitude != null && !evalResult?.matched && locationStatus !== 'in_range'"
          class="flex items-center justify-center gap-2 py-3 rounded-2xl font-black text-sm transition-all"
          style="background: #eff6ff; color: #2563eb; border: 2px solid #bfdbfe; border-bottom: 4px solid #93c5fd"
          @click="goNavigate(selectedTask)">
          <PhNavigationArrow :size="18" weight="duotone" color="#3b82f6" />
          Navigate to Location
        </button>

        <!-- Camera button: disabled if task has location and user not in range -->
        <button v-if="!evalResult?.matched"
          class="btn-game text-base font-black flex items-center justify-center gap-2"
          :style="canTakePhoto ? '' : 'opacity: 0.4; pointer-events: none'"
          :disabled="!canTakePhoto"
          @click="triggerCamera">
          <PhCamera :size="20" weight="duotone" color="white" />
          {{ capturedPhoto ? 'Retake Photo' : 'Take a Photo!' }}
        </button>

        <button v-if="evalResult?.matched"
          class="btn-game text-base font-black flex items-center justify-center gap-2"
          @click="handleCompleteTask">
          <PhCheckCircle :size="20" weight="duotone" color="white" />
          Awesome! Claim XP!
        </button>

        <button class="text-sm font-bold text-gray-400 py-2" @click="closeConfirm">
          Not yet
        </button>
      </div>
    </div>

    <!-- Parks Series modal (navigate only, no camera) -->
    <div v-if="showParkModal"
      class="fixed inset-0 flex items-end justify-center z-50"
      style="background: rgba(0,0,0,0.4)"
      @click.self="closeParkModal">
      <div class="w-full max-w-md bg-white rounded-t-3xl p-6 flex flex-col gap-4"
        :style="`border-top: 4px solid ${parksSeries.borderBottomColor}`">

        <div class="flex items-start gap-3">
          <div class="w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0"
            :style="`background: ${parksSeries.iconBg}; border: 2px solid ${parksSeries.borderColor}; border-bottom: 3px solid ${parksSeries.borderBottomColor}`">
            <PhTree :size="28" weight="duotone" :color="parksSeries.color" />
          </div>
          <div class="flex-1">
            <p class="text-lg font-black text-gray-800">{{ selectedPark?.parkName }}</p>
            <p class="text-xs font-semibold text-gray-400 mt-0.5 leading-relaxed">
              {{ selectedPark?.recommendDescription || 'Explore this park and complete its trail to earn XP!' }}
            </p>
          </div>
        </div>

        <!-- Park info tags -->
        <div class="flex flex-wrap gap-1.5">
          <span v-if="selectedPark?.parkHa"
            class="park-modal-tag" style="background:#f0fdfa;color:#0d9488">
            <PhMapPin :size="11" weight="bold" />
            {{ selectedPark.parkHa }}
          </span>
          <span v-if="selectedPark?.transportAccessibility"
            class="park-modal-tag" style="background:#eff6ff;color:#2563eb">
            {{ selectedPark.transportAccessibility }}
          </span>
          <span v-if="selectedPark?.taskRichness"
            class="park-modal-tag" style="background:#fdf4ff;color:#a21caf">
            {{ selectedPark.taskRichness }}
          </span>
        </div>

        <!-- XP reward banner -->
        <div class="bg-amber-50 rounded-2xl p-3 flex items-center gap-2"
          style="border: 2px solid #fde68a; border-bottom: 3px solid #fbbf24">
          <PhLightning :size="20" weight="duotone" color="#f59e0b" />
          <p class="text-sm font-black text-amber-700">
            Complete this park to earn +50 XP!
          </p>
        </div>

        <!-- Distance / proximity banner — same style & wording as the
             other series so the first card no longer looks different -->
        <div class="rounded-2xl p-3 flex items-center gap-2"
          :style="parkProximity === 'in_range'
            ? 'background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #34d399'
            : parkProximity === 'checking'
              ? 'background: #f8fafc; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'
              : 'background: #fff7ed; border: 2px solid #fed7aa; border-bottom: 3px solid #fdba74'">
          <PhSpinner v-if="parkProximity === 'checking'" :size="16" weight="duotone" color="#94a3b8" class="animate-spin" />
          <PhMapPin v-else-if="parkProximity === 'in_range'" :size="16" weight="duotone" color="#16a34a" />
          <PhWarning v-else :size="16" weight="duotone" color="#f59e0b" />
          <p class="text-xs font-bold"
            :style="parkProximity === 'in_range' ? 'color:#16a34a' : parkProximity === 'checking' ? 'color:#94a3b8' : 'color:#ea580c'">
            {{ parkProximityMessage }}
          </p>
        </div>

        <!-- Navigate to Location: this is a plain park with no route, so
             it uses the same map-navigation flow as the task cards
             (destination pin + Cancel), not the adventure route view. -->
        <button
          class="btn-game text-base font-black flex items-center justify-center gap-2"
          @click="navigateToPark">
          <PhNavigationArrow :size="20" weight="duotone" color="white" />
          Navigate to Location
        </button>

        <button class="text-sm font-bold text-gray-400 py-2" @click="closeParkModal">
          Not yet
        </button>
      </div>
    </div>

  </div>

  <!-- Onboarding -->
  <Teleport to="body">
    <div v-if="showOb" class="fixed inset-0 z-[999]" @click="nextOb">
      <div class="absolute inset-0 bg-black/50"></div>
      <div v-if="obStep === 0" class="ob-card-tasks" style="top: 28%; left: 50%; transform: translateX(-50%);">
        <div class="ob-arrow-up-t"></div>
        <div class="flex items-center gap-2 mb-2">
          <PhStarFour :size="20" weight="duotone" color="#10b981" />
          <p class="text-base font-black text-gray-800">Series Gallery</p>
        </div>
        <p class="text-sm text-gray-600 leading-relaxed">
          Each series (Nature, Urban, Art) has a collection of photo tasks at specific locations. Complete all tasks in a series to unlock its badge!
        </p>
        <div class="flex items-center justify-between mt-4">
          <span class="text-xs font-bold text-gray-400">1 / 2</span>
          <button class="ob-next-t" @click.stop="nextOb">Next</button>
        </div>
      </div>
      <div v-if="obStep === 1" class="ob-card-tasks" style="top: 50%; left: 50%; transform: translateX(-50%);">
        <div class="flex items-center gap-2 mb-2">
          <PhCamera :size="20" weight="duotone" color="#3b82f6" />
          <p class="text-base font-black text-gray-800">Complete Tasks</p>
        </div>
        <p class="text-sm text-gray-600 leading-relaxed">
          Scroll sideways to see all tasks in a series. Tap a card to take a photo. Some tasks have multiple locations to visit. The progress bar tracks how far you are!
        </p>
        <div class="flex items-center justify-between mt-4">
          <span class="text-xs font-bold text-gray-400">2 / 2</span>
          <button class="ob-next-t" @click.stop="nextOb">Got it!</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useProgressStore } from '../stores/progress'
import { loadCompletedTaskIds, markTaskCompleted } from '../stores/progress'
import { useNavigationStore } from '../stores/navigation'
import { useWeatherStore } from '../stores/weather'
import { trackEvent } from '../services/analytics'
import {
  PhLightning, PhCheckCircle, PhXCircle, PhSpinner,
  PhCamera, PhMedal, PhSeal, PhTree, PhBuildings, PhPaintBrush,
  PhMapPin, PhCaretRight, PhNavigationArrow, PhWarning, PhStarFour,
  PhCompass, PhX, PhCheck
} from '@phosphor-icons/vue'

const BASE_URL = 'https://tp35-kids-c7cxb7b7f7akbkah.southeastasia-01.azurewebsites.net'
const SERIES_TASKS_KEY = 'snaphunter_series_all_tasks'
const PROXIMITY_RADIUS = 200 // meters

const router = useRouter()
const progressStore = useProgressStore()
const navStore = useNavigationStore()
const weather = useWeatherStore()

const allTasks = ref([])
const loadingTasks = ref(false)

// ─── Parks Series state ─────────────────────────────────────
const PARKS_CACHE_KEY = 'snaphunter_all_parks_cache'
const allParks = ref([])
const parksLoading = ref(false)

// Onboarding
const OB_KEY = 'snaphunter_tasks_onboarded'
const showOb = ref(false)
const obStep = ref(0)
function nextOb() {
  if (obStep.value < 1) { obStep.value++ } else { showOb.value = false; localStorage.setItem(OB_KEY, 'true') }
}
const showModal = ref(false)
const showLocationPicker = ref(false)
const selectedTask = ref(null)
const selectedSeries = ref(null)
const selectedGroup = ref(null)
const fileInput = ref(null)
const capturedPhoto = ref(null)
const evaluating = ref(false)
const evalResult = ref(null)

// Park Series modal state
const showParkModal = ref(false)
const selectedPark = ref(null)
const parkDistance = ref(null) // meters, or null while resolving
// Proximity state for the park modal banner, mirroring the task
// modal's locationStatus so the first card looks identical to the
// other series: 'checking' | 'in_range' | 'out_of_range' | 'error'
const parkProximity = ref('checking')
const parkProximityMessage = ref('Checking your location...')

// Location verification state
const locationStatus = ref('checking') // 'checking' | 'in_range' | 'out_of_range' | 'error'
const locationMessage = ref('Checking your location...')
const userLat = ref(null)
const userLng = ref(null)

const canTakePhoto = computed(() => {
  // If task has no location requirement, always allow
  if (selectedTask.value?.latitude == null) return true
  return locationStatus.value === 'in_range'
})

const seriesList = [
  {
    id: 1,
    name: 'Nature Series',
    description: 'Explore the natural world',
    icon: PhTree,
    color: '#16a34a',
    iconBg: '#f0fdf4',
    borderColor: '#bbf7d0',
    borderBottomColor: '#34d399',
  },
  {
    id: 2,
    name: 'Urban Series',
    description: 'Discover your city',
    icon: PhBuildings,
    color: '#3b82f6',
    iconBg: '#eff6ff',
    borderColor: '#bfdbfe',
    borderBottomColor: '#93c5fd',
  },
  {
    id: 3,
    name: 'Art Series',
    description: 'Find beauty everywhere',
    icon: PhPaintBrush,
    color: '#a855f7',
    iconBg: '#faf5ff',
    borderColor: '#e9d5ff',
    borderBottomColor: '#d8b4fe',
  },
]

// Parks Series — special series shown first. It lists nearby parks from
// /api/all-parks and marks the ones the user has already visited (shared
// with the Home page Recommended Parks + Park Adventure flow).
const parksSeries = {
  id: 'parks',
  name: 'Parks Series',
  description: 'Visit parks around you',
  icon: PhCompass,
  color: '#0d9488',
  iconBg: '#f0fdfa',
  borderColor: '#99f6e4',
  borderBottomColor: '#5eead4',
}

// Set of visited park ids (as strings) from the shared progress store
const visitedParkIds = computed(() => {
  const set = new Set()
  for (const r of progressStore.visitedParkRecords) set.add(String(r.parkId))
  return set
})

// Park cards for the Parks Series, with a `done` flag derived from
// the shared visited records.
const parkCards = computed(() =>
  allParks.value.map(p => ({
    ...p,
    done: visitedParkIds.value.has(String(p.parkId)),
  }))
)

const parksDoneCount = computed(() =>
  parkCards.value.filter(p => p.done).length
)

const parksProgress = computed(() => {
  if (!parkCards.value.length) return 0
  return Math.round((parksDoneCount.value / parkCards.value.length) * 100)
})

const parksSeriesCompleted = computed(() =>
  parkCards.value.length > 0 && parkCards.value.every(p => p.done)
)

// ─── Active navigation (shared store) ───────────────────────
// Tasks / parks reached via the Map keep a live route. The matching
// card here is pulled to the front of its OWN series (series structure
// unchanged), recoloured, and its corner button becomes a red X that
// cancels — the only way to end navigation.
function parkCardNavId(p) { return `park-${p.parkId}` }
function taskNavId(t) { return `task-${t.taskId}` }
function groupNavId(group) {
  // A group is "navigating" when any of its (not-done) tasks is the
  // active target — matches how a single-location card maps 1:1 and a
  // multi-location card maps to whichever stop the user set off to.
  const navId = navStore.navigatingId
  if (!navId) return null
  const hit = group.tasks.find(t => taskNavId(t) === navId)
  return hit ? navId : null
}

const sortedParkCards = computed(() => {
  const list = [...parkCards.value]
  const navId = navStore.navigatingId
  if (!navId) return list
  const idx = list.findIndex(p => parkCardNavId(p) === navId)
  if (idx > 0) {
    const [active] = list.splice(idx, 1)
    list.unshift(active)
  }
  return list
})

function cancelNavigation() {
  navStore.cancel()
}

function parkSizeShort(parkHa) {
  if (!parkHa) return 'Park'
  if (parkHa.toLowerCase().includes('large')) return 'Large'
  if (parkHa.toLowerCase().includes('medium')) return 'Medium'
  if (parkHa.toLowerCase().includes('small')) return 'Small'
  return parkHa
}

// ─── Persistence helpers ────────────────────────────────────

function getTodayKey() {
  return new Date().toISOString().slice(0, 10)
}

function loadCachedSeriesTasks() {
  try {
    const saved = JSON.parse(localStorage.getItem(SERIES_TASKS_KEY) || 'null')
    if (saved && saved.date === getTodayKey()) {
      return saved.tasks
    }
  } catch { /* ignore */ }
  return null
}

function saveCachedSeriesTasks(tasks) {
  localStorage.setItem(SERIES_TASKS_KEY, JSON.stringify({
    date: getTodayKey(),
    tasks,
  }))
}

// ─── Fetch tasks ────────────────────────────────────────────

// Overwrite each task's `done` from the permanent completed-task set.
// This set — not the day-scoped SERIES_TASKS_KEY cache — is the source
// of truth for completion, so a finished task stays finished across
// the daily list refresh and regardless of whether it was completed
// here or on a Park Adventure route. Applied on BOTH paths (fresh
// fetch and cached read) so the two can never disagree.
function applyCompletedFlags(tasks) {
  const doneIds = loadCompletedTaskIds()
  return tasks.map(t => ({ ...t, done: doneIds.has(String(t.taskId)) }))
}

async function fetchAllTasks() {
  loadingTasks.value = true
  try {
    const results = await Promise.all(
      seriesList.map(s =>
        axios.get(`${BASE_URL}/api/tasks/series/all`, { params: { seriesId: s.id } })
          .then(res => res.data)
          .catch(() => [])
      )
    )
    allTasks.value = applyCompletedFlags(results.flat())
    saveCachedSeriesTasks(allTasks.value)
  } catch (e) {
    console.error('Failed to fetch tasks:', e)
  } finally {
    loadingTasks.value = false
  }
}

async function loadOrFetchAllTasks() {
  const cached = loadCachedSeriesTasks()
  if (cached && cached.length > 0) {
    // Cache holds only the task LIST for today; completion comes from
    // the permanent set, so re-apply it (the cache's own `done` flags
    // may be stale relative to routes completed since it was written).
    allTasks.value = applyCompletedFlags(cached)
  } else {
    await fetchAllTasks()
  }
}

// ─── Fetch all parks (Parks Series) ─────────────────────────

function loadCachedParks() {
  try {
    const saved = JSON.parse(localStorage.getItem(PARKS_CACHE_KEY) || 'null')
    if (saved && saved.date === getTodayKey() && Array.isArray(saved.parks)) {
      return saved.parks
    }
  } catch { /* ignore */ }
  return null
}

function saveCachedParks(parks) {
  localStorage.setItem(PARKS_CACHE_KEY, JSON.stringify({
    date: getTodayKey(),
    parks,
  }))
}

async function fetchAllParks() {
  parksLoading.value = true
  try {
    const pos = await new Promise((resolve, reject) => {
      if (!navigator.geolocation) { reject(new Error('no geo')); return }
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true, timeout: 10000,
      })
    })
    const res = await axios.get(`${BASE_URL}/api/all-parks`, {
      params: {
        latitude: pos.coords.latitude,
        longitude: pos.coords.longitude,
      },
      timeout: 8000,
    })
    allParks.value = Array.isArray(res.data) ? res.data : []
    saveCachedParks(allParks.value)
  } catch (e) {
    console.error('Failed to fetch all parks:', e)
    // Fall back to any cached list so the series is not empty
    const cached = loadCachedParks()
    if (cached) allParks.value = cached
  } finally {
    parksLoading.value = false
  }
}

async function loadOrFetchAllParks() {
  const cached = loadCachedParks()
  if (cached && cached.length > 0) {
    allParks.value = cached
    // Refresh quietly in the background to get latest distances
    fetchAllParks()
  } else {
    await fetchAllParks()
  }
}

// ─── Task grouping helpers ──────────────────────────────────

function getSeriesTasks(seriesId) {
  return allTasks.value.filter(t => t.seriesId === seriesId)
}

function getGroupedTasks(seriesId) {
  const tasks = getSeriesTasks(seriesId)
  const map = new Map()
  for (const task of tasks) {
    const key = task.taskName
    if (!map.has(key)) map.set(key, [])
    map.get(key).push(task)
  }
  const groups = []
  for (const [taskName, groupTasks] of map) {
    const doneCount = groupTasks.filter(t => t.done).length
    groups.push({
      key: `${seriesId}-${taskName}`,
      taskName,
      tasks: groupTasks,
      totalReward: groupTasks.reduce((sum, t) => sum + t.rewardPoint, 0),
      doneCount,
      allDone: doneCount === groupTasks.length,
      someDone: doneCount > 0 && doneCount < groupTasks.length,
    })
  }
  return groups
}

// Same groups, but the one currently being navigated is pulled to the
// front of THIS series (series order/structure otherwise unchanged).
function getSortedGroupedTasks(seriesId) {
  const groups = getGroupedTasks(seriesId)
  const navId = navStore.navigatingId
  if (!navId) return groups
  const idx = groups.findIndex(g => g.tasks.some(t => taskNavId(t) === navId))
  if (idx > 0) {
    const [active] = groups.splice(idx, 1)
    groups.unshift(active)
  }
  return groups
}

function seriesCompletedCount(seriesId) {
  return getSeriesTasks(seriesId).filter(t => t.done).length
}

function seriesProgress(seriesId) {
  const tasks = getSeriesTasks(seriesId)
  if (!tasks.length) return 0
  return Math.round((seriesCompletedCount(seriesId) / tasks.length) * 100)
}

function seriesCompleted(seriesId) {
  const tasks = getSeriesTasks(seriesId)
  return tasks.length > 0 && tasks.every(t => t.done)
}

// ─── Location verification ─────────────────────────────────

/**
 * Calculate distance between two GPS coordinates in meters (Haversine formula)
 */
function getDistanceMeters(lat1, lng1, lat2, lng2) {
  const R = 6371000 // Earth radius in meters
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat / 2) ** 2
    + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180)
    * Math.sin(dLng / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function checkProximity() {
  if (selectedTask.value?.latitude == null) {
    locationStatus.value = 'in_range'
    locationMessage.value = 'No location required'
    return
  }

  locationStatus.value = 'checking'
  locationMessage.value = 'Checking your location...'

  if (!navigator.geolocation) {
    locationStatus.value = 'error'
    locationMessage.value = 'GPS not available on this device'
    return
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      userLat.value = pos.coords.latitude
      userLng.value = pos.coords.longitude
      const dist = getDistanceMeters(
        pos.coords.latitude, pos.coords.longitude,
        selectedTask.value.latitude, selectedTask.value.longitude
      )
      if (dist <= PROXIMITY_RADIUS) {
        locationStatus.value = 'in_range'
        locationMessage.value = `You're at the task location (${Math.round(dist)}m away)`
      } else {
        locationStatus.value = 'out_of_range'
        const distKm = dist >= 1000 ? `${(dist / 1000).toFixed(1)}km` : `${Math.round(dist)}m`
        locationMessage.value = `You're ${distKm} away. Please go to the task location first!`
      }
    },
    (err) => {
      locationStatus.value = 'error'
      if (err.code === 1) {
        locationMessage.value = 'Location access denied. Please enable GPS to take photos.'
      } else {
        locationMessage.value = 'Could not get your location. Please try again.'
      }
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
  )
}

// ─── Modal interaction ──────────────────────────────────────

function handleCardClick(group, series) {
  if (group.allDone) return
  selectedSeries.value = series
  if (group.tasks.length === 1) {
    const task = group.tasks[0]
    if (task.done) return
    openConfirm(task, series)
  } else {
    selectedGroup.value = group
    showLocationPicker.value = true
  }
}

function openConfirmFromLocation(task) {
  if (task.done) return
  showLocationPicker.value = false
  openConfirm(task, selectedSeries.value)
}

function closeLocationPicker() {
  showLocationPicker.value = false
  selectedGroup.value = null
}

function openConfirm(task, series) {
  if (task.done) return
  selectedTask.value = task
  selectedSeries.value = series
  capturedPhoto.value = null
  evalResult.value = null
  locationStatus.value = 'checking'
  showModal.value = true
  trackEvent('task_start', { taskId: task.taskId, taskName: task.taskName })
  // Start location check
  checkProximity()
}

function closeConfirm() {
  showModal.value = false
  selectedTask.value = null
  capturedPhoto.value = null
  evalResult.value = null
  locationStatus.value = 'checking'
  if (selectedGroup.value) {
    refreshSelectedGroup()
    showLocationPicker.value = true
  }
}

function refreshSelectedGroup() {
  if (!selectedGroup.value) return
  const seriesId = selectedSeries.value?.id
  const groups = getGroupedTasks(seriesId)
  const updated = groups.find(g => g.taskName === selectedGroup.value.taskName)
  if (updated) selectedGroup.value = updated
}

function triggerCamera() {
  capturedPhoto.value = null
  evalResult.value = null
  fileInput.value?.click()
}

async function handlePhotoCapture(event) {
  const file = event.target.files?.[0]
  if (!file) return
  capturedPhoto.value = URL.createObjectURL(file)
  evaluating.value = true
  evalResult.value = null
  progressStore.addPhoto()
  trackEvent('photo_taken', { taskId: selectedTask.value?.taskId, taskName: selectedTask.value?.taskName })
  try {
    const formData = new FormData()
    formData.append('taskId', selectedTask.value.taskId)
    formData.append('file', file)
    const res = await axios.post(`${BASE_URL}/api/tasks/evaluate`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    evalResult.value = res.data
  } catch (e) {
    evalResult.value = { matched: false, reason: 'Something went wrong. Please try again.' }
  } finally {
    evaluating.value = false
    event.target.value = ''
  }
}

function handleCompleteTask() {
  const task = allTasks.value.find(t => t.taskId === selectedTask.value.taskId)
  if (task) {
    // Record in the permanent set first. `isNew` is false if this task
    // was somehow already completed (e.g. finished earlier on a route),
    // so we don't double-count XP / streak for the same task.
    const isNew = markTaskCompleted(task.taskId)

    task.done = true

    if (isNew) {
      // Update progress
      progressStore.completeTask(task.rewardPoint || 10)

      // Check sunny day badge
      if (weather.desc === 'Clear sky') {
        progressStore.completeSunnyTask()
      }
    }

    // Check series completion (safe to re-check even if not new)
    const seriesId = task.seriesId
    if (seriesId) {
      const seriesKey = seriesId === 1 ? 'nature' : seriesId === 2 ? 'urban' : 'art'
      if (seriesCompleted(seriesId)) {
        progressStore.earnBadge(seriesKey)
      }
    }

    // Persist to localStorage
    saveCachedSeriesTasks(allTasks.value)

    trackEvent('task_complete', {
      taskId: task.taskId,
      taskName: task.taskName,
      xpEarned: task.rewardPoint || 10,
    })
  }
  closeConfirm()
}

function goNavigate(task) {
  if (task.latitude == null || task.longitude == null) return
  router.push({
    path: '/map',
    query: {
      navLat: String(task.latitude),
      navLng: String(task.longitude),
      navName: task.taskName,
      navId: `task-${task.taskId}`,
    }
  })
}

// ─── Parks Series interaction ───────────────────────────────

function openParkModal(park) {
  selectedPark.value = park
  parkDistance.value = park.distance != null ? Math.round(park.distance) : null
  showParkModal.value = true
  parkProximity.value = 'checking'
  parkProximityMessage.value = 'Checking your location...'
  trackEvent('park_open', { parkId: park.parkId, parkName: park.parkName })

  if (!navigator.geolocation || park.latitude == null || park.longitude == null) {
    // No GPS / no coords: fall back to the API distance, shown the same
    // orange "go there first" way as an out-of-range task.
    applyParkProximity(parkDistance.value)
    return
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const d = Math.round(getDistanceMeters(
        pos.coords.latitude, pos.coords.longitude,
        park.latitude, park.longitude
      ))
      parkDistance.value = d
      applyParkProximity(d)
    },
    () => {
      // Keep API-provided distance; still classify it for the banner.
      applyParkProximity(parkDistance.value)
    },
    { enableHighAccuracy: true, timeout: 8000, maximumAge: 30000 }
  )
}

// Classify a distance into the same banner states/wording the task
// cards use, so the Parks Series first card stops looking different.
function applyParkProximity(distMeters) {
  if (distMeters == null) {
    parkProximity.value = 'out_of_range'
    parkProximityMessage.value = 'Please go to the park location first!'
    return
  }
  if (distMeters <= PROXIMITY_RADIUS) {
    parkProximity.value = 'in_range'
    parkProximityMessage.value = `You're at the park (${distMeters}m away)`
  } else {
    parkProximity.value = 'out_of_range'
    const distText = distMeters >= 1000 ? `${(distMeters / 1000).toFixed(1)}km` : `${distMeters}m`
    parkProximityMessage.value = `You're ${distText} away. Please go to the task location first!`
  }
}

function closeParkModal() {
  showParkModal.value = false
  selectedPark.value = null
  parkDistance.value = null
  parkProximity.value = 'checking'
  parkProximityMessage.value = 'Checking your location...'
}

function navigateToPark() {
  const park = selectedPark.value
  if (!park || park.latitude == null || park.longitude == null) return
  trackEvent('park_navigate', { parkId: park.parkId, parkName: park.parkName })
  showParkModal.value = false
  router.push({
    path: '/map',
    query: {
      navLat: String(park.latitude),
      navLng: String(park.longitude),
      navName: park.parkName,
      navId: `park-${park.parkId}`,
    }
  })
}

onMounted(() => {
  progressStore.init()
  navStore.load()
  loadOrFetchAllTasks()
  loadOrFetchAllParks()
  if (!localStorage.getItem(OB_KEY)) { showOb.value = true; obStep.value = 0 }
})
</script>

<style>
.ob-card-tasks { position: absolute; width: calc(100% - 32px); max-width: 360px; padding: 20px; border-radius: 24px; background: white; border: 2px solid #d1fae5; border-bottom: 4px solid #34d399; box-shadow: 0 8px 32px rgba(0,0,0,0.2); z-index: 1000; font-family: var(--font-game), system-ui, sans-serif }
.ob-next-t { padding: 8px 20px; border-radius: 14px; background: linear-gradient(135deg, #10b981, #059669); border: none; border-bottom: 3px solid #047857; color: white; font-size: 13px; font-weight: 900; cursor: pointer; font-family: var(--font-game), system-ui, sans-serif }
.ob-arrow-up-t { position: absolute; top: -10px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-bottom: 10px solid white }
.park-modal-tag { display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px; border-radius: 9px; font-size: 11px; font-weight: 800; line-height: 1; font-family: var(--font-game), system-ui, sans-serif }
</style>