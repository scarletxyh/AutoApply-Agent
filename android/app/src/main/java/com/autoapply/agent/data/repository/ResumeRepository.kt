package com.autoapply.agent.data.repository

import com.autoapply.agent.data.remote.ResumeResponse
import com.autoapply.agent.data.remote.ApiService
import okhttp3.MultipartBody
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ResumeRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun getResumes(): List<ResumeResponse> {
        return apiService.getResumes()
    }

    suspend fun uploadResume(filePart: MultipartBody.Part): ResumeResponse {
        return apiService.uploadResume(filePart)
    }

    suspend fun deleteResume(resumeId: Int) {
        apiService.deleteResume(resumeId)
    }
}
