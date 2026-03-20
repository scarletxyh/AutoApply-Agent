package com.autoapply.agent.ui.screens

import android.net.Uri
import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

data class ResumeCategory(
    val name: String,
    val items: List<String>,
)

data class ResumeUiState(
    val fileUri: Uri? = null,
    val fileName: String? = null,
    val categories: List<ResumeCategory> = emptyList(),
)

@HiltViewModel
class ResumeViewModel @Inject constructor() : ViewModel() {

    private val _uiState = MutableStateFlow(ResumeUiState())
    val uiState: StateFlow<ResumeUiState> = _uiState.asStateFlow()

    fun onFileSelected(uri: Uri?, name: String?) {
        _uiState.value = _uiState.value.copy(
            fileUri = uri,
            fileName = name,
            // Placeholder categories — would be parsed by backend in the future
            categories = if (uri != null) {
                listOf(
                    ResumeCategory("Education", listOf("BS Computer Science — UCSD")),
                    ResumeCategory(
                        "Experience",
                        listOf("Software Engineer Intern — Google", "SDE Intern — Amazon"),
                    ),
                    ResumeCategory(
                        "Skills",
                        listOf("Python", "Kotlin", "Java", "SQL", "Docker", "Kubernetes"),
                    ),
                    ResumeCategory(
                        "Projects",
                        listOf("AutoApply-Agent", "ML Pipeline Framework"),
                    ),
                )
            } else {
                emptyList()
            },
        )
    }

    fun clearResume() {
        _uiState.value = ResumeUiState()
    }
}
