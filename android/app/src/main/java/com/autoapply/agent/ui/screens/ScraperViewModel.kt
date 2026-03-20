package com.autoapply.agent.ui.screens

import android.util.Patterns
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.autoapply.agent.data.remote.ScrapeRunResponse
import com.autoapply.agent.data.repository.JobRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ScraperUiState(
    val url: String = "",
    val urlError: String? = null,
    val isSubmitting: Boolean = false,
    val scrapeRun: ScrapeRunResponse? = null,
    val resultJobId: Int? = null,
    val errorMessage: String? = null,
)

@HiltViewModel
class ScraperViewModel @Inject constructor(
    private val repository: JobRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(ScraperUiState())
    val uiState: StateFlow<ScraperUiState> = _uiState.asStateFlow()

    fun onUrlChanged(url: String) {
        _uiState.value = _uiState.value.copy(url = url, urlError = null, errorMessage = null)
    }

    fun isValidUrl(): Boolean {
        val url = _uiState.value.url.trim()
        if (url.isBlank()) {
            _uiState.value = _uiState.value.copy(urlError = "URL cannot be empty")
            return false
        }
        if (!Patterns.WEB_URL.matcher(url).matches()) {
            _uiState.value = _uiState.value.copy(urlError = "Please enter a valid URL")
            return false
        }
        return true
    }

    fun submitUrl() {
        if (!isValidUrl()) return

        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                isSubmitting = true,
                errorMessage = null,
                scrapeRun = null,
                resultJobId = null,
            )
            try {
                val scrapeRun = repository.scrapeUrl(url = _uiState.value.url.trim())
                _uiState.value = _uiState.value.copy(scrapeRun = scrapeRun)

                // Poll for completion
                pollScrapeStatus(scrapeRun.id)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isSubmitting = false,
                    errorMessage = e.message ?: "Failed to submit scrape request",
                )
            }
        }
    }

    private suspend fun pollScrapeStatus(runId: Int) {
        var attempts = 0
        while (attempts < 60) {
            delay(2000)
            try {
                val status = repository.getScrapeStatus(runId)
                _uiState.value = _uiState.value.copy(scrapeRun = status)

                when (status.status) {
                    "completed" -> {
                        // Fetch the latest jobs to find the one we just scraped
                        val jobs = repository.fetchAndCacheJobs()
                        val latestJob = jobs.firstOrNull()
                        _uiState.value = _uiState.value.copy(
                            isSubmitting = false,
                            resultJobId = latestJob?.id,
                        )
                        return
                    }
                    "failed" -> {
                        _uiState.value = _uiState.value.copy(
                            isSubmitting = false,
                            errorMessage = status.errorMessage ?: "Scrape failed",
                        )
                        return
                    }
                }
            } catch (e: Exception) {
                // Continue polling on transient errors
            }
            attempts++
        }
        _uiState.value = _uiState.value.copy(
            isSubmitting = false,
            errorMessage = "Scrape timed out",
        )
    }

    fun resetState() {
        _uiState.value = ScraperUiState()
    }
}
