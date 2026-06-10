package com.secureiot.doorlock_api.repository;

import com.secureiot.doorlock_api.model.SystemSetting;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

@Repository
public interface SystemSettingRepository extends JpaRepository<SystemSetting, Integer> {
    
    // We explicitly tell Java to use "system_settings" to match your Workbench table
    @Query(value = "SELECT * FROM system_settings WHERE setting_name = ?1", nativeQuery = true)
    SystemSetting findBySettingName(String settingName);
}