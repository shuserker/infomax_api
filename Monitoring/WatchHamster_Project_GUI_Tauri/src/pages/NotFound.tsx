import React from 'react'
import {
  Box,
  Heading,
  Text,
  Button,
  VStack,
  Icon,
  Container,
  useColorModeValue,
} from '@chakra-ui/react'
import { FiHome, FiAlertTriangle } from 'react-icons/fi'
import { useNavigate } from 'react-router-dom'

const NotFound: React.FC = () => {
  const navigate = useNavigate()
  const bgColor = useColorModeValue('gray.50', 'gray.900')


  return (
    <Box minH="100vh" bg={bgColor} display="flex" alignItems="center">
      <Container maxW="md" textAlign="center">
        <VStack spacing={8}>
          <Icon as={FiAlertTriangle} boxSize={20} color="orange.400" />
          
          <VStack spacing={4}>
            <Heading size="2xl" color="gray.700" _dark={{ color: 'gray.200' }}>
              404
            </Heading>
            <Heading size="lg" color="gray.600" _dark={{ color: 'gray.300' }}>
              페이지를 찾을 수 없습니다
            </Heading>
            <Text color="gray.500" _dark={{ color: 'gray.400' }} maxW="sm">
              요청하신 페이지가 존재하지 않거나 이동되었을 수 있습니다.
              아래 버튼을 클릭하여 대시보드로 돌아가세요.
            </Text>
          </VStack>

          <VStack spacing={4} w="full">
            <Button
              leftIcon={<FiHome />}
              colorScheme="blue"
              size="lg"
              onClick={() => navigate('/')}
              w="full"
              maxW="200px"
            >
              대시보드로 이동
            </Button>
            
            <Button
              variant="ghost"
              onClick={() => navigate(-1)}
              size="sm"
            >
              이전 페이지로 돌아가기
            </Button>
          </VStack>
        </VStack>
      </Container>
    </Box>
  )
}

export default NotFound