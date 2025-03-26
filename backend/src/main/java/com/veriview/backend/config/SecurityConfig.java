// import org.springframework.context.annotation.Bean;
// import org.springframework.context.annotation.Configuration;
// import org.springframework.security.config.annotation.web.builders.HttpSecurity;
// import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
// import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
// import org.springframework.web.cors.CorsConfiguration;
// import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
// import org.springframework.web.filter.CorsFilter;

// @Configuration
// @EnableWebSecurity
// public class SecurityConfig extends WebSecurityConfigurerAdapter {

//     @Override
//     protected void configure(HttpSecurity http) throws Exception {
//     //CORS (Cross-Origin Resource Sharing)를 활성화하고 CSRF (Cross-Site Request Forgery) 보호 기능을 비활성화
//         http.cors().and().csrf().disable();
//     }

//     @Bean
//     public CorsFilter corsFilter() {
//         UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
//         CorsConfiguration config = new CorsConfiguration();
//         config.setAllowCredentials(true);
//         config.addAllowedOrigin("http://localhost:3000"); //리액트 포트 번호 
//         config.addAllowedHeader("*");
//         config.addAllowedMethod("*");
//         source.registerCorsConfiguration("/**", config); //모든 경로에 대해 CORS 구성을 등록
//         return new CorsFilter(source); 
//     }
// }