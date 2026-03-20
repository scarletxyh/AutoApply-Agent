package com.autoapply.agent.ui.screens

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

data class ProfileUiState(
    val fullName: String = "",
    val email: String = "",
    val phone: String = "",
    val linkedin: String = "",
    val github: String = "",
    val skills: List<String> = emptyList(),
    val newSkill: String = "",
    val experiences: List<WorkExperience> = listOf(WorkExperience()),
    val isSaved: Boolean = false,
)

data class WorkExperience(
    val company: String = "",
    val title: String = "",
    val duration: String = "",
    val description: String = "",
)

@HiltViewModel
class ProfileViewModel @Inject constructor() : ViewModel() {

    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    fun onFieldChanged(field: String, value: String) {
        _uiState.value = when (field) {
            "fullName" -> _uiState.value.copy(fullName = value)
            "email" -> _uiState.value.copy(email = value)
            "phone" -> _uiState.value.copy(phone = value)
            "linkedin" -> _uiState.value.copy(linkedin = value)
            "github" -> _uiState.value.copy(github = value)
            "newSkill" -> _uiState.value.copy(newSkill = value)
            else -> _uiState.value
        }
    }

    fun addSkill() {
        val skill = _uiState.value.newSkill.trim()
        if (skill.isNotBlank() && skill !in _uiState.value.skills) {
            _uiState.value = _uiState.value.copy(
                skills = _uiState.value.skills + skill,
                newSkill = "",
            )
        }
    }

    fun removeSkill(skill: String) {
        _uiState.value = _uiState.value.copy(
            skills = _uiState.value.skills - skill,
        )
    }

    fun updateExperience(index: Int, experience: WorkExperience) {
        val updated = _uiState.value.experiences.toMutableList()
        if (index < updated.size) {
            updated[index] = experience
        }
        _uiState.value = _uiState.value.copy(experiences = updated)
    }

    fun addExperience() {
        _uiState.value = _uiState.value.copy(
            experiences = _uiState.value.experiences + WorkExperience(),
        )
    }

    fun removeExperience(index: Int) {
        if (_uiState.value.experiences.size > 1) {
            val updated = _uiState.value.experiences.toMutableList()
            updated.removeAt(index)
            _uiState.value = _uiState.value.copy(experiences = updated)
        }
    }

    fun saveProfile() {
        // TODO: Persist to local storage / backend
        _uiState.value = _uiState.value.copy(isSaved = true)
    }
}
