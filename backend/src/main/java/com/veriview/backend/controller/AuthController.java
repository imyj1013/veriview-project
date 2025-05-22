package com.veriview.backend.controller;

import com.veriview.backend.model.LoginRequest;
import com.veriview.backend.model.SignupRequest;
import com.veriview.backend.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/signup")
    public ResponseEntity<?> signup(@RequestBody SignupRequest request) {
        try {
            authService.signup(request);
            return ResponseEntity.ok(Map.of("message", "회원가입 성공"));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/check-username/{userId}")
    public ResponseEntity<?> checkUsername(@PathVariable String userId) {
        boolean available = authService.isUsernameAvailable(userId);
        if (available) {
            return ResponseEntity.ok(Map.of("available", true));
        } else {
            return ResponseEntity.ok(Map.of("available", false, "message", "이미 존재하는 아이디입니다."));
        }
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {
        try {
            String token = authService.login(request);
            return ResponseEntity.ok(Map.of("message", "로그인 성공", "access_token", token));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(401).body(Map.of("error", e.getMessage()));
        }
    }
}