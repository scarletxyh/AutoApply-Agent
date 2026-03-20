package com.autoapply.agent.ui.screens

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

enum class AgentState {
    IDLE, RUNNING, PAUSED, NEEDS_INPUT
}

data class AutoApplyUiState(
    val isAutoSubmit: Boolean = false,
    val agentState: AgentState = AgentState.IDLE,
    val uncertainField: String? = null,
    val processedCount: Int = 0,
)

@HiltViewModel
class AutoApplyViewModel @Inject constructor() : ViewModel() {

    private val _uiState = MutableStateFlow(AutoApplyUiState())
    val uiState: StateFlow<AutoApplyUiState> = _uiState.asStateFlow()

    fun toggleAutoSubmit(enabled: Boolean) {
        _uiState.value = _uiState.value.copy(isAutoSubmit = enabled)
    }

    fun startAgent() {
        _uiState.value = _uiState.value.copy(agentState = AgentState.RUNNING)
        // TODO: Wire to backend when implemented
    }

    fun pauseAgent() {
        _uiState.value = _uiState.value.copy(agentState = AgentState.PAUSED)
    }

    fun stopAgent() {
        _uiState.value = _uiState.value.copy(agentState = AgentState.IDLE)
    }

    fun simulateUncertainField(field: String) {
        _uiState.value = _uiState.value.copy(
            agentState = AgentState.NEEDS_INPUT,
            uncertainField = field,
        )
    }

    fun resolveUncertainField() {
        _uiState.value = _uiState.value.copy(
            agentState = AgentState.RUNNING,
            uncertainField = null,
            processedCount = _uiState.value.processedCount + 1,
        )
    }
}
