package com.autoapply.agent.di

import android.content.Context
import androidx.room.Room
import com.autoapply.agent.data.local.AppDatabase
import com.autoapply.agent.data.local.JobDao
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.inMemoryDatabaseBuilder(
            context,
            AppDatabase::class.java
        ).fallbackToDestructiveMigration().build()
    }

    @Provides
    fun provideJobDao(db: AppDatabase): JobDao = db.jobDao()
}
