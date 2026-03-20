package com.autoapply.agent.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "jobs")
data class JobEntity(
    @PrimaryKey val id: Int,
    val title: String,
    val companyId: Int,
    val companyName: String? = null,
    val location: String? = null,
    val descriptionRaw: String? = null,
    val descriptionSummary: String? = null,
    val requirementsMustHave: String? = null,
    val requirementsNiceToHave: String? = null,
    val requirementsYearsExperience: String? = null,
    val cohort: String,
    val seniorityLevel: String? = null,
    val salaryMin: Double? = null,
    val salaryMax: Double? = null,
    val url: String? = null,
    val isActive: Boolean,
    val scrapedAt: String? = null,
    val createdAt: String,
    val updatedAt: String,
)
