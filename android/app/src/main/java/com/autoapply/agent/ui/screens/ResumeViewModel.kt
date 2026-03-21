package com.autoapply.agent.ui.screens

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.autoapply.agent.data.remote.ResumeResponse
import com.autoapply.agent.data.repository.ResumeRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody
import javax.inject.Inject

data class ResumeUiState(
    val resumes: List<ResumeResponse> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class ResumeViewModel @Inject constructor(
    private val repository: ResumeRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ResumeUiState(isLoading = true))
    val uiState: StateFlow<ResumeUiState> = _uiState.asStateFlow()

    init {
        fetchResumes()
    }

    fun fetchResumes() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            try {
                val list = repository.getResumes()
                _uiState.value = _uiState.value.copy(resumes = list, isLoading = false)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(error = e.message, isLoading = false)
            }
        }
    }

    fun deleteResume(id: Int) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            try {
                repository.deleteResume(id)
                fetchResumes()
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(error = "Failed to delete: ${e.message}", isLoading = false)
            }
        }
    }

    fun uploadResume(uri: Uri, context: Context) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            try {
                val contentResolver = context.contentResolver
                
                var fileName = "resume.tex"
                contentResolver.query(uri, null, null, null, null)?.use { cursor ->
                    val nameIndex = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                    if (cursor.moveToFirst() && nameIndex != -1) {
                        fileName = cursor.getString(nameIndex)
                    }
                }

                val inputStream = contentResolver.openInputStream(uri)
                val bytes = inputStream?.readBytes()
                inputStream?.close()

                if (bytes == null) {
                    _uiState.value = _uiState.value.copy(error = "Could not cleanly buffer the file bytes", isLoading = false)
                    return@launch
                }

                val requestBody = bytes.toRequestBody("application/x-tex".toMediaTypeOrNull())
                val part = MultipartBody.Part.createFormData("file", fileName, requestBody)

                repository.uploadResume(part)
                fetchResumes()
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(error = "Network transmission failed: ${e.message}", isLoading = false)
            }
        }
    }
}
