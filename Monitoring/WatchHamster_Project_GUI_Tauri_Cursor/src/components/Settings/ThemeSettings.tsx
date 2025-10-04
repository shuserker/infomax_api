import React, { useState } from 'react'
import {
  VStack,
  HStack,
  FormControl,
  FormLabel,
  FormHelperText,
  Switch,
  Select,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Button,
  Box,
  Text,
  Grid,
  GridItem,
  Input,
  useColorMode,
  useToast,
  Badge,
  Divider,
  SimpleGrid,
} from '@chakra-ui/react'
import { AppSettings } from '../../hooks/useSettings'

interface ThemeSettingsProps {
  settings: AppSettings
  onSettingChange: (key: keyof AppSettings, value: any) => void
  onNestedSettingChange: (path: string, value: any) => void
}

const ThemeSettings: React.FC<ThemeSettingsProps> = ({
  settings,
  onSettingChange,
  onNestedSettingChange,
}) => {
  const { colorMode, toggleColorMode } = useColorMode()
  const toast = useToast()
  const [previewMode, setPreviewMode] = useState<'light' | 'dark' | null>(null)

  // 미리 정의된 색상 팔레트
  const colorPalettes = {
    posco: {
      name: 'POSCO 기본',
      primary: '#003d82',
      secondary: '#0066cc',
      accent: '#ff6b35',
    },
    modern: {
      name: '모던 블루',
      primary: '#2563eb',
      secondary: '#3b82f6',
      accent: '#06b6d4',
    },
    warm: {
      name: '따뜻한 톤',
      primary: '#dc2626',
      secondary: '#ea580c',
      accent: '#f59e0b',
    },
    nature: {
      name: '자연 친화',
      primary: '#059669',
      secondary: '#10b981',
      accent: '#84cc16',
    },
    purple: {
      name: '퍼플 테마',
      primary: '#7c3aed',
      secondary: '#8b5cf6',
      accent: '#a855f7',
    },
  }

  const handleThemeChange = (theme: 'light' | 'dark' | 'system') => {
    onSettingChange('theme', theme)
    
    // 실제 색상 모드 변경
    if (theme === 'light' && colorMode === 'dark') {
      toggleColorMode()
    } else if (theme === 'dark' && colorMode === 'light') {
      toggleColorMode()
    } else if (theme === 'system') {
      // 시스템 설정에 따라 자동 변경
      const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if ((systemPrefersDark && colorMode === 'light') || (!systemPrefersDark && colorMode === 'dark')) {
        toggleColorMode()
      }
    }

    toast({
      title: '테마 변경됨',
      description: `${theme === 'light' ? '라이트' : theme === 'dark' ? '다크' : '시스템'} 모드로 변경되었습니다`,
      status: 'success',
      duration: 2000,
      isClosable: true,
    })
  }

  const handleColorPaletteSelect = (palette: typeof colorPalettes.posco) => {
    onNestedSettingChange('customColors.primary', palette.primary)
    onNestedSettingChange('customColors.secondary', palette.secondary)
    onNestedSettingChange('customColors.accent', palette.accent)

    toast({
      title: '색상 팔레트 적용됨',
      description: `${palette.name} 팔레트가 적용되었습니다`,
      status: 'success',
      duration: 2000,
      isClosable: true,
    })
  }

  const handleCustomColorChange = (colorType: 'primary' | 'secondary' | 'accent', color: string) => {
    onNestedSettingChange(`customColors.${colorType}`, color)
  }

  const resetToDefaultColors = () => {
    handleColorPaletteSelect(colorPalettes.posco)
    onSettingChange('poscoTheme', true)
  }

  const previewTheme = (mode: 'light' | 'dark') => {
    setPreviewMode(mode)
    setTimeout(() => setPreviewMode(null), 2000)
  }

  return (
    <Card>
      <CardHeader>
        <Heading size="md">테마 설정</Heading>
      </CardHeader>
      <CardBody>
        <VStack spacing={6} align="stretch">
          {/* 테마 모드 설정 */}
          <FormControl>
            <FormLabel>테마 모드</FormLabel>
            <Select
              value={settings.theme}
              onChange={e => handleThemeChange(e.target.value as 'light' | 'dark' | 'system')}
            >
              <option value="light">라이트 모드</option>
              <option value="dark">다크 모드</option>
              <option value="system">시스템 설정 따르기</option>
            </Select>
            <FormHelperText>
              애플리케이션의 전체적인 색상 테마를 설정합니다
            </FormHelperText>
          </FormControl>

          {/* 테마 미리보기 */}
          <Box>
            <Text fontWeight="medium" mb={3}>테마 미리보기</Text>
            <HStack spacing={4}>
              <Button
                size="sm"
                variant="outline"
                onClick={() => previewTheme('light')}
                bg={previewMode === 'light' ? 'blue.50' : undefined}
              >
                라이트 모드 미리보기
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => previewTheme('dark')}
                bg={previewMode === 'dark' ? 'gray.700' : undefined}
                color={previewMode === 'dark' ? 'white' : undefined}
              >
                다크 모드 미리보기
              </Button>
            </HStack>
          </Box>

          <Divider />

          {/* POSCO 기업 테마 */}
          <FormControl display="flex" alignItems="center">
            <FormLabel htmlFor="posco-theme" mb="0" flex="1">
              POSCO 기업 테마
              <Badge ml={2} colorScheme="blue">권장</Badge>
            </FormLabel>
            <Switch
              id="posco-theme"
              isChecked={settings.poscoTheme}
              onChange={e => onSettingChange('poscoTheme', e.target.checked)}
              colorScheme="posco"
            />
          </FormControl>

          {/* 색상 팔레트 선택 */}
          <Box>
            <Text fontWeight="medium" mb={3}>미리 정의된 색상 팔레트</Text>
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
              {Object.entries(colorPalettes).map(([key, palette]) => (
                <Card
                  key={key}
                  size="sm"
                  cursor="pointer"
                  onClick={() => handleColorPaletteSelect(palette)}
                  _hover={{ shadow: 'md' }}
                  border={
                    settings.customColors.primary === palette.primary
                      ? '2px solid'
                      : '1px solid'
                  }
                  borderColor={
                    settings.customColors.primary === palette.primary
                      ? 'blue.500'
                      : 'gray.200'
                  }
                >
                  <CardBody>
                    <VStack spacing={2}>
                      <Text fontSize="sm" fontWeight="medium">
                        {palette.name}
                      </Text>
                      <HStack spacing={2}>
                        <Box
                          w={6}
                          h={6}
                          bg={palette.primary}
                          borderRadius="md"
                          title="Primary"
                        />
                        <Box
                          w={6}
                          h={6}
                          bg={palette.secondary}
                          borderRadius="md"
                          title="Secondary"
                        />
                        <Box
                          w={6}
                          h={6}
                          bg={palette.accent}
                          borderRadius="md"
                          title="Accent"
                        />
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>
              ))}
            </SimpleGrid>
          </Box>

          <Divider />

          {/* 커스텀 색상 설정 */}
          <Box>
            <Text fontWeight="medium" mb={3}>커스텀 색상 설정</Text>
            <Grid templateColumns="repeat(3, 1fr)" gap={4}>
              <GridItem>
                <FormControl>
                  <FormLabel fontSize="sm">주 색상 (Primary)</FormLabel>
                  <HStack>
                    <Input
                      type="color"
                      value={settings.customColors.primary}
                      onChange={e => handleCustomColorChange('primary', e.target.value)}
                      w={12}
                      h={10}
                      p={1}
                      border="none"
                    />
                    <Input
                      value={settings.customColors.primary}
                      onChange={e => handleCustomColorChange('primary', e.target.value)}
                      placeholder="#003d82"
                      size="sm"
                    />
                  </HStack>
                </FormControl>
              </GridItem>

              <GridItem>
                <FormControl>
                  <FormLabel fontSize="sm">보조 색상 (Secondary)</FormLabel>
                  <HStack>
                    <Input
                      type="color"
                      value={settings.customColors.secondary}
                      onChange={e => handleCustomColorChange('secondary', e.target.value)}
                      w={12}
                      h={10}
                      p={1}
                      border="none"
                    />
                    <Input
                      value={settings.customColors.secondary}
                      onChange={e => handleCustomColorChange('secondary', e.target.value)}
                      placeholder="#0066cc"
                      size="sm"
                    />
                  </HStack>
                </FormControl>
              </GridItem>

              <GridItem>
                <FormControl>
                  <FormLabel fontSize="sm">강조 색상 (Accent)</FormLabel>
                  <HStack>
                    <Input
                      type="color"
                      value={settings.customColors.accent}
                      onChange={e => handleCustomColorChange('accent', e.target.value)}
                      w={12}
                      h={10}
                      p={1}
                      border="none"
                    />
                    <Input
                      value={settings.customColors.accent}
                      onChange={e => handleCustomColorChange('accent', e.target.value)}
                      placeholder="#ff6b35"
                      size="sm"
                    />
                  </HStack>
                </FormControl>
              </GridItem>
            </Grid>

            <HStack mt={4} spacing={3}>
              <Button size="sm" variant="outline" onClick={resetToDefaultColors}>
                기본 색상으로 복원
              </Button>
              <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                색상 변경 사항은 저장 후 적용됩니다
              </Text>
            </HStack>
          </Box>

          {/* 색상 미리보기 */}
          <Box>
            <Text fontWeight="medium" mb={3}>현재 색상 미리보기</Text>
            <Card size="sm">
              <CardBody>
                <VStack spacing={3}>
                  <HStack spacing={4} w="full">
                    <Button
                      bg={settings.customColors.primary}
                      color="white"
                      _hover={{ opacity: 0.8 }}
                      size="sm"
                    >
                      Primary Button
                    </Button>
                    <Button
                      bg={settings.customColors.secondary}
                      color="white"
                      _hover={{ opacity: 0.8 }}
                      size="sm"
                    >
                      Secondary Button
                    </Button>
                    <Button
                      bg={settings.customColors.accent}
                      color="white"
                      _hover={{ opacity: 0.8 }}
                      size="sm"
                    >
                      Accent Button
                    </Button>
                  </HStack>
                  
                  <Box w="full" p={3} bg="gray.50" _dark={{ bg: 'gray.700' }} borderRadius="md">
                    <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                      이 색상들이 버튼, 링크, 강조 요소에 사용됩니다
                    </Text>
                  </Box>
                </VStack>
              </CardBody>
            </Card>
          </Box>
        </VStack>
      </CardBody>
    </Card>
  )
}

export default ThemeSettings