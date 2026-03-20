package com.autoapply.agent.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Dashboard
import androidx.compose.material.icons.filled.Description
import androidx.compose.material.icons.filled.RocketLaunch
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Work
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.autoapply.agent.ui.screens.AutoApplyScreen
import com.autoapply.agent.ui.screens.DashboardScreen
import com.autoapply.agent.ui.screens.JobDetailScreen
import com.autoapply.agent.ui.screens.JobsScreen
import com.autoapply.agent.ui.screens.ProfileScreen
import com.autoapply.agent.ui.screens.ResumeScreen
import com.autoapply.agent.ui.screens.ScraperScreen

// ── Route definitions ────────────────────────────────────────────────────────

object Routes {
    const val SCRAPER = "scraper"
    const val RESUME = "resume"
    const val JOBS = "jobs"
    const val JOB_DETAIL = "jobs/{jobId}"
    const val PROFILE = "profile"
    const val AUTO_APPLY = "auto_apply"
    const val DASHBOARD = "dashboard"

    fun jobDetail(jobId: Int) = "jobs/$jobId"
}

// ── Bottom nav items ─────────────────────────────────────────────────────────

data class BottomNavItem(
    val route: String,
    val label: String,
    val icon: ImageVector,
)

val bottomNavItems = listOf(
    BottomNavItem(Routes.SCRAPER, "Scraper", Icons.Default.Search),
    BottomNavItem(Routes.RESUME, "Resume", Icons.Default.Description),
    BottomNavItem(Routes.JOBS, "Jobs", Icons.Default.Work),
    BottomNavItem(Routes.AUTO_APPLY, "Auto-Apply", Icons.Default.RocketLaunch),
    BottomNavItem(Routes.DASHBOARD, "Dashboard", Icons.Default.Dashboard),
)

// ── Navigation host ──────────────────────────────────────────────────────────

@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    // Hide bottom bar on detail screens
    val showBottomBar = bottomNavItems.any { it.route == currentDestination?.route }

    Scaffold(
        bottomBar = {
            if (showBottomBar) {
                NavigationBar {
                    bottomNavItems.forEach { item ->
                        NavigationBarItem(
                            icon = { Icon(item.icon, contentDescription = item.label) },
                            label = { Text(item.label) },
                            selected = currentDestination?.hierarchy?.any {
                                it.route == item.route
                            } == true,
                            onClick = {
                                navController.navigate(item.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                        )
                    }
                }
            }
        },
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Routes.SCRAPER,
            modifier = Modifier.padding(innerPadding),
        ) {
            composable(Routes.SCRAPER) {
                ScraperScreen(
                    onNavigateToJobDetail = { jobId ->
                        navController.navigate(Routes.jobDetail(jobId))
                    },
                )
            }
            composable(Routes.RESUME) {
                ResumeScreen()
            }
            composable(Routes.JOBS) {
                JobsScreen(
                    onNavigateToDetail = { jobId ->
                        navController.navigate(Routes.jobDetail(jobId))
                    },
                )
            }
            composable(
                route = Routes.JOB_DETAIL,
                arguments = listOf(navArgument("jobId") { type = NavType.IntType }),
            ) { backStackEntry ->
                val jobId = backStackEntry.arguments?.getInt("jobId") ?: return@composable
                JobDetailScreen(
                    jobId = jobId,
                    onNavigateBack = { navController.popBackStack() },
                )
            }
            composable(Routes.AUTO_APPLY) {
                AutoApplyScreen(
                    onNavigateToProfile = {
                        navController.navigate(Routes.PROFILE)
                    },
                )
            }
            composable(Routes.PROFILE) {
                ProfileScreen(
                    onNavigateBack = { navController.popBackStack() },
                )
            }
            composable(Routes.DASHBOARD) {
                DashboardScreen()
            }
        }
    }
}
