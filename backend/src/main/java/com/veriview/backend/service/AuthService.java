package com.veriview.backend.service;

import com.veriview.backend.entity.User;
import com.veriview.backend.model.LoginRequest;
import com.veriview.backend.model.SignupRequest;
import com.veriview.backend.repository.UserRepository;
import com.veriview.backend.util.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;

    public void signup(SignupRequest request) {
        if (userRepository.existsByUserId(request.user_id)) {
            throw new IllegalArgumentException("이미 존재하는 아이디입니다.");
        }

        User user = new User();
        user.setUserId(request.user_id);
        user.setPassword(passwordEncoder.encode(request.password));
        user.setName(request.name);
        user.setEmail(request.email);

        userRepository.save(user);
    }

    public String login(LoginRequest request) {
        User user = userRepository.findByUserId(request.user_id)
                .orElseThrow(() -> new IllegalArgumentException("아이디 또는 비밀번호가 잘못되었습니다."));

        if (!passwordEncoder.matches(request.password, user.getPassword())) {
            throw new IllegalArgumentException("아이디 또는 비밀번호가 잘못되었습니다.");
        }

        return jwtTokenProvider.createToken(user.getUserId());
    }

    public boolean isUsernameAvailable(String userId) {
        return !userRepository.existsByUserId(userId);
    }
}