package com.autoapply.agent.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface JobDao {

    @Query("SELECT * FROM jobs ORDER BY id DESC")
    fun getAll(): Flow<List<JobEntity>>

    @Query("SELECT * FROM jobs WHERE id = :id")
    suspend fun getById(id: Int): JobEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(jobs: List<JobEntity>)

    @Query("DELETE FROM jobs")
    suspend fun deleteAll()
}
