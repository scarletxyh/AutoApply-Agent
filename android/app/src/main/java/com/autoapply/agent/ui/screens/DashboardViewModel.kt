package com.autoapply.agent.ui.screens

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.autoapply.agent.data.repository.JobRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class DashboardUiState(
    val totalJobsScraped: Int = 0,
    val totalApplicationsSent: Int = 0,
    val pendingActions: Int = 0,
    val isLoading: Boolean = true,
)

@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val repository: JobRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(DashboardUiState())
    val uiState: StateFlow<DashboardUiState> = _uiState.asStateFlow()

    init {
        loadDashboard()
    }

    private fun loadDashboard() {
        viewModelScope.launch {
            repository.getCachedJobs().collect { jobs ->
                _uiState.value = _uiState.value.copy(
                    totalJobsScraped = jobs.size,
                    // Placeholder values for features not yet backed
                    totalApplicationsSent = 0,
                    pendingActions = 0,
                    isLoading = false,
                )
            }
        }
    }
}
