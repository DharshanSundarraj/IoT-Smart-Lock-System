package com.secureiot.doorlock_api.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.secureiot.doorlock_api.model.AccessLog;
import org.springframework.stereotype.Repository;

@Repository
public interface AccessLogRepository extends JpaRepository<AccessLog, Integer> {
}