package com.autoapply.agent.ui.screens

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.autoapply.agent.data.local.JobEntity
import com.autoapply.agent.data.repository.JobRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

data class JobsUiState(
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
)

@HiltViewModel
class JobsViewModel @Inject constructor(
    private val repository: JobRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(JobsUiState())
    val uiState: StateFlow<JobsUiState> = _uiState.asStateFlow()

    val jobs: StateFlow<List<JobEntity>> = repository.getCachedJobs()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    init {
        refreshJobs()
    }

    fun refreshJobs() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
            try {
                repository.fetchAndCacheJobs()
                _uiState.value = _uiState.value.copy(isLoading = false)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "Failed to load jobs. Showing cached data.",
                )
            }
        }
    }
}
